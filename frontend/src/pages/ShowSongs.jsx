import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

function ShowSongs() {
    const [songs, setSongs] = useState([]);
    const location = useLocation();

    // read the query param: "private" or "public"
    const params = new URLSearchParams(location.search);
    const type = params.get("type") || "private"; // default private

    useEffect(() => {
        async function loadSongs() {
            const endpoint =
                type === "public"
                    ? "/api/songs/public"
                    : "/api/songs/private";

            const res = await fetch(
                `https://lofi-app-dc75.onrender.com${endpoint}`,
                { credentials: "include" }
            );

            const data = await res.json();
            setSongs(data);
        }

        loadSongs();
    }, [type]); // reload when type changes

    return (
        <>
            <h2>{type === "public" ? "Public Songs" : "Your Songs"}</h2>

            {songs.map(song => (
                <div key={song.id}>
                    <h3>{song.title}</h3>
                    <audio src={song.audio_url} controls />
                </div>
            ))}
        </>
    );
}

export default ShowSongs;
