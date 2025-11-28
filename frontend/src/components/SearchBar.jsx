import { useState, useEffect } from "react";

function SearchBar (props) {
    const [query, setQuery] = useState("");
    const [isFocused, setIsFocused] = useState(false);

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

    const styles = {
        container: {
            position: 'sticky',
            top: 0,
            zIndex: 100,
            background: 'linear-gradient(180deg, rgba(10,10,10,1) 0%, rgba(10,10,10,0.98) 80%, rgba(10,10,10,0.95) 100%)',
            padding: '20px 24px',
            borderBottom: '2px solid rgba(29, 185, 84, 0.3)',
            boxShadow: '0 4px 12px rgba(29, 185, 84, 0.1), 0 2px 4px rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(10px)'
        },
        form: {
            maxWidth: '800px',
            margin: '0 auto',
            display: 'flex',
            gap: '12px'
        },
        input: {
            flex: 1,
            padding: '16px 24px',
            fontSize: '16px',
            borderRadius: '500px',
            border: '2px solid rgba(29, 185, 84, 0.4)',
            backgroundColor: 'rgba(20, 20, 20, 0.8)',
            color: '#ffffff',
            transition: 'all 0.3s ease',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)'
        }
    };

    return (
        <div style={styles.container}>
            <style>{`
                .search-input:focus {
                    outline: none;
                    border-color: rgba(29, 185, 84, 0.8);
                    box-shadow: 0 0 0 3px rgba(29, 185, 84, 0.2), 0 2px 8px rgba(0, 0, 0, 0.2);
                }
                .search-input::placeholder {
                    color: rgba(179, 179, 179, 0.8);
                }
            `}</style>
            <form onSubmit={handleSubmit} style={styles.form}>
                <input
                    className="search-input"
                    style={styles.input}
                    type="text"
                    value={query}
                    onChange={handleInputChange}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    placeholder={!isFocused ? (props.disabled ? "Generating song..." : "Give a prompt to generate a song.") : ""}
                    disabled={props.disabled}
                />
            </form>
        </div>
    );
}

export default SearchBar