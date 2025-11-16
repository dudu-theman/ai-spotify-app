import { Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import ShowSongs from "./pages/ShowSongs.jsx";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/api/songs" element={<ShowSongs/>}/>
      </Routes>
    </>
  );
}

export default App;
