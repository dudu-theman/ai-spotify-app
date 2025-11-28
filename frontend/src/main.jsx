import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { AudioPlayerProvider } from "./contexts/AudioPlayerContext.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <AudioPlayerProvider>
      <App />
    </AudioPlayerProvider>
  </BrowserRouter>
);
