import { useEffect, useState } from "react";

function ShowSongs () {

    const [songs, setSongs] = useState([]);

    useEffect(() => {
        async function loadSongs() {
            const res = await fetch("https://lofi-app-dc75.onrender.com/api/songs/private")
            const data = await res.json();
            setSongs(data);
        }

        loadSongs();
    },[])

    return (
        <>
            {songs.map(song => (
                <div key={song.id}>
                    <h3>{song.title}</h3>
                    <h3>{song.audio_url}</h3>
                    <audio src={song.audio_url} controls />
                </div>
            ))

            }
        </>
    );
}

export default ShowSongs;