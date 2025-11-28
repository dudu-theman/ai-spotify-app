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

    const styles = {
        container: {
            position: 'sticky',
            top: 0,
            zIndex: 100,
            backgroundColor: 'var(--bg-primary)',
            padding: '16px 24px',
            borderBottom: '1px solid var(--border-color)',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
        },
        form: {
            maxWidth: '800px',
            margin: '0 auto',
            display: 'flex',
            gap: '12px'
        },
        input: {
            flex: 1,
            padding: '14px 20px',
            fontSize: '16px',
            borderRadius: '500px',
            border: '2px solid var(--border-color)',
            backgroundColor: 'var(--bg-elevated)',
            color: 'var(--text-primary)',
            transition: 'border-color 0.2s ease'
        }
    };

    return (
        <div style={styles.container}>
            <form onSubmit={handleSubmit} style={styles.form}>
                <input
                    style={styles.input}
                    type="text"
                    value={query}
                    onChange={handleInputChange}
                    placeholder={props.disabled ? "Generating song..." : "Give a prompt to generate a song."}
                    disabled={props.disabled}
                />
            </form>
        </div>
    );
}

export default SearchBar