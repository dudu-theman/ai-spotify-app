import { useState, useEffect } from "react";

function SearchBar (props) {
    const [query, setQuery] = useState("");

    const handleInputChange = (e) => {
        setQuery(e.target.value)
    }

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        props.onSearch(query)
    }

    useEffect(() => {
        if (!props.disabled) setQuery("");
    }, [props.disabled])

    return (
        <form onSubmit={handleSubmit}>
            <input 
              type="text"
              value={query}
              onChange={handleInputChange}
              placeholder={props.disabled ? "Generating song..." : "Give a prompt to generate a song."}
              disabled={props.disabled}
            />
        </form>
    );
}

export default SearchBar