import { useNavigate } from "react-router-dom"

function ViewSongsButton() {
    const navigate = useNavigate();

    const handleClick = () => {
        navigate("/api/songs");
    }

    return (
        <button onClick = {handleClick}>View Songs</button>
    );
}

export default ViewSongsButton;