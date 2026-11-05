export default function Footer() {
  return (
    <footer className="site-footer">
      <p>
        FireGuard AI — built for Neural Storm 2026 (Green Planet track).
        Detection model:{" "}
        <a href="https://huggingface.co/seawsurf/fire_yolo" target="_blank" rel="noreferrer">
          seawsurf/fire_yolo
        </a>{" "}
        · Dataset:{" "}
        <a href="https://doi.org/10.1080/10095020.2024.2347922" target="_blank" rel="noreferrer">
          FASDD_CV
        </a>
      </p>
    </footer>
  );
}
