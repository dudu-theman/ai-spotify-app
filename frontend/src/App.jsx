import { Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import ShowSongs from "./pages/ShowSongs.jsx";
import SearchBar from "./components/SearchBar.jsx"

const BASE_URL =  import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

function App() {

  const handleSearch = async (query) => {
    try {
      const res = await fetch(`${BASE_URL}/generate?q=${query}`, { method: "POST" });
      const data = await res.json();
      console.log("Results:", data);
      alert("Song is generating");
    } catch (error) {
      console.error("Error fetching search results", error);
      alert("Error generating song");
    }
  }

  return (
    <>
      <SearchBar onSearch={handleSearch}/>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/showsongs" element={<ShowSongs/>}/>
      </Routes>
    </>
  );
}

export default App;
