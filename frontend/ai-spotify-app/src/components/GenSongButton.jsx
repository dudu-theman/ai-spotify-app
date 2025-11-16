const BASE_URL =  import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

const handleClick = async () => {
    console.log("THE BASE URL IS");
    console.log(`${BASE_URL}/generate`);
    try {
        const res = await fetch(`${BASE_URL}/generate`, { method: "POST" });
        const data = await res.json();
        console.log("Song generation triggered:", data);
        alert("Song generation Triggered. Songs will appear when ready.");
    } catch (err) {
        console.error(err);
        alert("Error generating song.");
    }
    
};

function GenSongButton() {

    return (
        <button onClick={handleClick}>Generate Song</button>
    );
}

export default GenSongButton