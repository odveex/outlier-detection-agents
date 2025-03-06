"""
Task processing utilities for outlier detection and rule integration.

This module provides functions for:
- Loading and initializing ML models for outlier detection
- Performing outlier detection on datasets
- Extracting rules from fitted models
- Integrating expert knowledge with detected outliers
"""

import base64
import logging
import json
import traceback
from io import BytesIO
from typing import Tuple, List, Dict, Any, Union, Optional

import pandas as pd
import matplotlib.pyplot as plt
from crewai.crew import CrewOutput

# Configure matplotlib
plt.switch_backend('Agg')

# Model imports
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from imodels import FIGSClassifier, OptimalTreeClassifier, GreedyTreeClassifier

# Local imports
from utils.redis import serialize_list, redis_connection
from utils.tree_utils_figs import create_tree, extract_rules, trunc_output
from utils.tree_utils import parse_tree_to_rules
from utils.rules_utils import apply_rules_to_dataset
from crew.crew import RulesExtractionAndIntegrationCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define constants
REDIS_TASK_DATA_DB = 1
REDIS_OUTLIER_RESULTS_DB = 2
REDIS_INTEGRATED_RESULTS_DB = 4


def load_outlier_model(data_algorithm: str) -> Tuple[Any, str]:
    """
    Load the appropriate outlier detection model based on algorithm name.
    
    Args:
        data_algorithm: Name of the outlier detection algorithm to use
        
    Returns:
        Tuple containing:
            - The initialized model object
            - Status string ('success' or 'failed')
    """
    logger.info(f"Loading outlier detection model: {data_algorithm}")
    status = 'success'
    model = None
    
    try:
        if data_algorithm == 'LocalOutlierFactor':
            model = LocalOutlierFactor()
        elif data_algorithm == 'IsolationForest':
            model = IsolationForest()
        elif data_algorithm == 'OneClassSVM':
            model = OneClassSVM()
        else:
            logger.error(f"Invalid outlier detection algorithm: {data_algorithm}")
            status = "failed"
    except Exception as exc:
        logger.error(f"Model initialization failed: {exc}", exc_info=True)
        status = "failed"
    
    return model, status


def load_model(rules_algorithm: str) -> Tuple[Any, str]:
    """
    Load the appropriate rules-based model based on algorithm name.
    
    Args:
        rules_algorithm: Name of the rules algorithm to use
        
    Returns:
        Tuple containing:
            - The initialized model object
            - Status string ('success' or 'failed')
    """
    logger.info(f"Loading rules-based model: {rules_algorithm}")
    status = 'success'
    model = None
    
    try:
        if rules_algorithm == 'FIGS':
            model = FIGSClassifier()
        elif rules_algorithm == 'OptimalTree':
            model = OptimalTreeClassifier()
        elif rules_algorithm == 'GreedyTree':
            model = GreedyTreeClassifier()
        else:
            logger.error(f"Invalid rules algorithm: {rules_algorithm}")
            status = "failed"
    except Exception as exc:
        logger.error(f"Model initialization failed: {exc}", exc_info=True)
        status = "failed"
    
    return model, status


def extract_rules_from_model(
    model: Any, 
    rules_algorithm: str, 
    df: pd.DataFrame
) -> Tuple[List[str], str]:
    """
    Extract rules from a fitted model.
    
    Args:
        model: Fitted model object
        rules_algorithm: Name of the rules algorithm used
        df: DataFrame with feature names
        
    Returns:
        Tuple containing:
            - List of extracted rules
            - Status string ('success' or 'failed')
    """
    rule_list = []
    status = 'success'
    
    try:
        if rules_algorithm == 'FIGS':
            tree_data = trunc_output(str(model)).split('\n')
            root = create_tree(tree_data)
            extract_rules(root, rule_list, '')
        else:
            # OptimalTree and GreedyTree handling
            columns = df.columns.tolist()
            tree_data = str(model)
            feature_no_to_column = {f"feature_{i}": columns[i] for i in range(len(columns))}

            rule_list_raw_feature = parse_tree_to_rules(tree_data)
            for rule in rule_list_raw_feature:
                for k, v in feature_no_to_column.items():
                    rule = rule.replace(k, v)
                rule_list.append(rule)
                
    except Exception as exc:
        logger.error(f"Rule extraction failed: {exc}", exc_info=True)
        status = "failed"
        
    return rule_list, status


def generate_model_image(model: Any) -> Tuple[Optional[str], str]:
    """
    Generate a visualization of the model's decision tree.
    
    Args:
        model: Fitted model object
        
    Returns:
        Tuple containing:
            - Base64 encoded image string or None if failed
            - Status string ('success' or 'failed')
    """
    status = 'success'
    image_base64 = None
    
    try:
        img_buffer = BytesIO()
        model.plot(filename=img_buffer, dpi=600)
        img_buffer.seek(0)
        image_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    except Exception as exc:
        logger.warning(f"Decision tree image generation failed: {exc}", exc_info=True)
        status = "failed"
        
    return image_base64, status


def store_results_in_redis(
    task_id: str, 
    db: int, 
    data: Dict[str, Any]
) -> str:
    """
    Store processing results in Redis.
    
    Args:
        task_id: Unique task identifier
        db: Redis database to use
        data: Dictionary of results to store
        
    Returns:
        Status string ('success' or 'failed')
    """
    status = 'success'
    try:
        with redis_connection(db=db) as r:
            r.set(task_id, json.dumps(data))
    except Exception as exc:
        logger.error(f"Failed to store results in Redis: {exc}", exc_info=True)
        status = "failed"
        
    return status


def outlier_detection_from_data(task_id: str) -> None:
    """
    Perform outlier detection on the provided data.
    
    This function:
    1. Retrieves task data from Redis
    2. Loads and applies the specified outlier detection algorithm
    3. Fits a rules-based model to explain the outliers
    4. Extracts human-readable rules from the model
    5. Stores results back to Redis
    
    Args:
        task_id: Unique task identifier
    """
    logger.info(f"Starting outlier detection for task {task_id}")

    try:
        # Retrieve task data
        with redis_connection(db=REDIS_TASK_DATA_DB) as r:
            registered_data = json.loads(r.get(task_id))

        data_algorithm = registered_data['data_algorithm']
        rules_algorithm = registered_data['rules_algorithm']
        data = registered_data['json_dict']

        # Initialize results
        status = "success"
        image_base64 = ""
        rules_serialized = serialize_list([])
        
        # Convert data to DataFrame
        try:
            df = pd.DataFrame(data).dropna()
        except Exception as exc:
            logger.error(f"DataFrame conversion failed: {exc}", exc_info=True)
            status = "failed"

        # Perform outlier detection
        if status != "failed":
            try:
                outlier_detection_model, status = load_outlier_model(data_algorithm)
                if status != "failed":
                    X = df.to_numpy()
                    outlier_labels = outlier_detection_model.fit_predict(X)
            except Exception as exc:
                logger.error(f"Outlier detection failed: {exc}", exc_info=True)
                status = "failed"

        # Load rules model
        model = None
        if status != "failed":
            model, status = load_model(rules_algorithm)

        # Fit rules model to outlier detection results
        if status != "failed" and model is not None:
            try:
                X = df.to_numpy()  # Ensure X is defined even if outlier detection was skipped
                model.fit(X, outlier_labels, feature_names=list(df.columns))
            except Exception as exc:
                logger.error(f"Model fitting failed: {exc}", exc_info=True)
                status = "failed"

        # Generate visualization
        if status != "failed" and model is not None:
            image_base64, img_status = generate_model_image(model)
            if img_status == "failed":
                image_base64 = ""

        # Extract rules from model
        rule_list = []
        if status != "failed" and model is not None:
            rule_list, status = extract_rules_from_model(model, rules_algorithm, df)
            rules_serialized = serialize_list(rule_list)

        # Store results in Redis
        store_results_in_redis(
            task_id, 
            REDIS_OUTLIER_RESULTS_DB,
            {
                "status": status,
                "image_url": f"data:image/png;base64,{image_base64}" if image_base64 else "",
                "rules": json.loads(rules_serialized)
            }
        )
        
    except Exception as exc:
        logger.error(f"Unexpected error in outlier detection: {exc}", exc_info=True)
        # Ensure we store failure status in Redis
        store_results_in_redis(
            task_id, 
            REDIS_OUTLIER_RESULTS_DB,
            {
                "status": "failed",
                "image_url": "",
                "rules": []
            }
        )


def extract_and_integrate_expert_rules(task_id: str) -> None:
    """
    Integrate expert knowledge with outlier detection results.
    
    This function:
    1. Retrieves task data and outlier detection results
    2. Passes expert text and outlier rules to the agent crew
    3. Integrates the resulting rules with the dataset
    4. Trains a new model on the integrated rules
    5. Extracts new human-readable rules from the model
    6. Stores results back to Redis
    
    Args:
        task_id: Unique task identifier
    """
    logger.info(f"Starting expert rule integration for task {task_id}")
    status = "success"
    image_base64 = ""

    try:
        # Retrieve task data
        with redis_connection(db=REDIS_TASK_DATA_DB) as r:
            registered_data = json.loads(r.get(task_id))
        
        # Wait for outlier detection results
        with redis_connection(db=REDIS_OUTLIER_RESULTS_DB) as r:
            data_outliers = r.get(task_id) # Retrieve the outlier detection from data results from Redis
    

        expert_text:str = registered_data['expert_text']
        rules_algorithm:str = registered_data['rules_algorithm']
        data:dict = registered_data['json_dict']

        df = pd.DataFrame(data).dropna()
        X = df.to_numpy()

        columns:list = df.columns.tolist()
        assert len(columns) == X.shape[1], "Columns and data shape mismatch"

        data_outliers_rules:list = json.loads(data_outliers)['rules']

        inputs = {
            'expert_text': expert_text,
            'rules': data_outliers_rules,
            'dataset_columns': columns
        }
        
        result:CrewOutput = RulesExtractionAndIntegrationCrew().crew().kickoff(inputs=inputs)
        output = result.raw

        try:
            rules_integrated_d:dict = json.loads(output)
            rules_integrated = rules_integrated_d['new_rules']
            new_df = apply_rules_to_dataset(rules_integrated, df)

            replaced = new_df["outlier"].replace({True: -1, False: 1})
            replaced = replaced.infer_objects(copy=False)
            outlier_labels = replaced.to_numpy()

            model = None
            if status != "failed":
                model, status = load_model(rules_algorithm)

            if status != "failed" and model is not None:
                try:
                    model.fit(X, outlier_labels, feature_names=columns)
                except Exception as exc:
                    logger.error(f"Model fitting failed: {exc}")
                    status = "failed"
            
            if status != "failed" and model is not None:    
                try:
                    img_buffer = BytesIO()
                    model.plot(filename=img_buffer, dpi=600)
                    img_buffer.seek(0)
                    image_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                except Exception as exc:
                    image_base64 = None
                    logging.error(f"Decision tree image generation failed: {exc}")

            rule_list = []
            if status != "failed" and model is not None:
                try:
                    if rules_algorithm == 'FIGS':
                        tree_data = trunc_output(str(model)).split('\n')
                        root = create_tree(tree_data)
                        extract_rules(root, rule_list, '')
                    else:
                        # OptimalTree and GreedyTree - nie wchodza feature names
                        columns = df.columns.tolist()
                        tree_data = str(model)
                        feature_no_to_column = {f"feature_{i}": columns[i] for i in range(len(columns))}

                        rule_list_raw_feature = parse_tree_to_rules(tree_data)
                        for rule in rule_list_raw_feature:
                            for k,v in feature_no_to_column.items():
                                rule = rule.replace(k, v)
                            
                            rule_list.append(rule)
                except Exception as exc:
                    logging.warning(f"Rule extraction failed: {exc}")
            
                try:
                    with redis_connection(db=REDIS_INTEGRATED_RESULTS_DB) as r:
                        r.set(task_id, json.dumps({
                            "status": status,
                            "image_url": f"data:image/png;base64,{image_base64}" if image_base64 else "",
                            "rules_integrated": json.loads(serialize_list(rules_integrated)), #integrated expert text & data
                            "new_rules":json.loads(serialize_list(rule_list)) #rules from tree created from outlier mark from rules_integrated
                        }))
                except Exception as exc:
                    logging.error(f"Failed to store results in Redis: {exc}")
            
        except Exception as exc:
            logging.error(f"Failed to parse new rules: {exc}")
    except Exception as exc:
        logger.error(f"Unexpected error in expert rule integration: {exc}", exc_info=True)
        # Ensure we store failure status in Redis
        store_results_in_redis(
            task_id, 
            REDIS_INTEGRATED_RESULTS_DB,
            {
                "status": "failed",
                "image_url": "",
                "rules_integrated": [],
                "new_rules": []
            }
        )