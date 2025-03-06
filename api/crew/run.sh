#!/bin/bash

# Stop existing container
docker stop crew-ai-rules || echo "No running container crew-ai"

# Build Docker image
docker build -t crew-ai .

# Run Docker container
docker run -v ./code:/app/code \
  --rm \
  --name crew-ai crew-ai \
  --expert_text="If truck speed > 120 km/h, then it is an outlier. When there is more than 100 high pressure compression cycles in a day then it is not normal." \
  --rules="IF Total no. compaction cycles > 100 AND Total no. compaction cycles with p>100 bar < 10 THEN outlier" \
  --rules="IF Total fuel consumed [dm3] > 40 and Motohours (PTO engaged) [h] < 2 then outlier" \
  --dataset_columns="date" \
  --dataset_columns="Motohours total [h]" \
  --dataset_columns="Motohours (PTO engaged) [h]" \
  --dataset_columns="Motohours stop (idle) [h]" \
  --dataset_columns="Motohours driving [h]" \
  --dataset_columns="Distance [km]" \
  --dataset_columns="Total no. compaction cycles" \
  --dataset_columns="Total no. compaction cycles with p>100 bar" \
  --dataset_columns="Total no. compaction cycles with p>150 bar" \
  --dataset_columns="Total fuel consumed [dm3]"