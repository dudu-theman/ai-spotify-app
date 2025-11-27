import { useNavigate } from "react-router-dom";

function ViewSongsButton() {
    const navigate = useNavigate();

    return (
        <>
            <button onClick={() => navigate("/showsongs?type=private")}>
                View Your Creations
            </button>

            <button onClick={() => navigate("/showsongs?type=public")}>
                Explore Existing Songs
            </button>
        </>
    );
}

export default ViewSongsButton;
