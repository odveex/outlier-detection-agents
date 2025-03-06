import { ImageMagnifier } from "./ImageMagnifier";

interface DecisionTreeImageProps {
  imageUrl: string;
}

export const DecisionTreeImage = (props: DecisionTreeImageProps) => {
  return (
    <div style={{ padding: "20px" }}>
      <ImageMagnifier
        src={props.imageUrl}
        magnifierHeight={180}
        magnifieWidth={180}
        width="350px"
        height="350px"
        zoomLevel={3}
      />
    </div>
  );
};
