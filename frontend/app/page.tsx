import Header from "@/components/Header";
import Footer from "@/components/Footer";
import FireMap from "@/components/FireMapClient";
import DetectForm from "@/components/DetectForm";
import RiskForm from "@/components/RiskForm";
import AlertSignup from "@/components/AlertSignup";

export default function HomePage() {
  return (
    <>
      <Header />

      <section className="hero">
        <h1>FireGuard AI</h1>
        <p>
          Early wildfire detection, risk prediction, and real-time alerts —
          in one dashboard.
        </p>
      </section>

      <main>
        <div className="sections">
          <section id="monitoring" className="card">
            <div className="card-header">
              <span className="step-index">1</span>
              <h2>Real-time Monitoring</h2>
            </div>
            <p className="card-description">
              Active hotspots from NASA FIRMS, shown on the map below.
            </p>
            <FireMap />
          </section>

          <section id="detection" className="card">
            <div className="card-header">
              <span className="step-index">2</span>
              <h2>Early Detection (Image)</h2>
            </div>
            <p className="card-description">
              Upload a photo and the model will flag fire or smoke with a
              confidence score.
            </p>
            <DetectForm />
          </section>

          <section id="risk" className="card">
            <div className="card-header">
              <span className="step-index">3</span>
              <h2>Risk Prediction</h2>
            </div>
            <p className="card-description">
              Pick a location, pull live weather, and get a fire-risk score.
            </p>
            <RiskForm />
          </section>

          <section id="alerts" className="card">
            <div className="card-header">
              <span className="step-index">4</span>
              <h2>Get Alerts for Your Area</h2>
            </div>
            <p className="card-description">
              Opt in to receive a push notification if a dangerous hotspot
              shows up near you.
            </p>
            <AlertSignup />
          </section>
        </div>
      </main>

      <Footer />
    </>
  );
}
