import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useState } from "react";
import HomePage from "./pages/HomePage.jsx";
import ShowSongs from "./pages/ShowSongs.jsx";
import SearchBar from "./components/SearchBar.jsx";
import AuthPage from "./pages/AuthPage.jsx";

const BASE_URL =  import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

function App() {

  const [isGenerating, setIsGenerating] = useState(false);

  const handleSearch = async (query) => {
    try {
      setIsGenerating(true);

      const res = await fetch(`${BASE_URL}/generate?q=${query}`, { 
        method: "POST",
        credentials: "include" 
      });

      const data = await res.json();
      console.log("Results:", data);
      alert("Song is generating. YOU WILL BE ALERTED WHEN SONG IS DONE GENERATING.");
      waitForCompletion(data.task_id, data.status);

    } catch (error) {
      console.error("Error fetching search results", error);
      alert("Error generating song");
      setIsGenerating(false);
    }
  };

  const waitForCompletion = (task_id, status) => {
    const check = async () => {
      try {
        const res = await fetch(`${BASE_URL}/task-status/${task_id}`, {
          credentials: "include",
        });
        const data = await res.json();

        if (status === "complete") {
          alert("Song finished generating!");
          setIsGenerating(false);
        } else if (status === "pending") {
          setTimeout(check, 2000); 
        } else {
          console.error("Unknown task status:", status);
          setIsGenerating(false);
        }
      } catch (err) {
        console.error("Error checking task status:", err);
        setTimeout(check, 2000); 
      }
    };
    check();
  };

  const location = useLocation();
  const showSearchBar = location.pathname !== "/auth";

  return (
    <>
      {showSearchBar && <SearchBar onSearch={handleSearch} disabled={isGenerating} />}
      <Routes>
        <Route path="/" element={<Navigate to="/auth" />} />
        <Route path="/auth" element={<AuthPage/>} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/showsongs" element={<ShowSongs/>}/>
      </Routes>
    </>
  );
}

export default App;
