/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                cyber: {
                    black: "#0a0a0f",
                    dark: "#12121a",
                    secondary: "#1a1a24",
                },
                neon: {
                    blue: "#00f3ff",
                    purple: "#bc13fe",
                    green: "#0afff0",
                    red: "#ff2a6d",
                },
            },
            boxShadow: {
                'neon-blue': '0 0 10px #00f3ff, 0 0 20px #00f3ff',
                'neon-purple': '0 0 10px #bc13fe, 0 0 20px #bc13fe',
                'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
            },
            fontFamily: {
                mono: ['"Orbitron"', 'monospace'], // For headers
                sans: ['"Inter"', 'sans-serif'], // For body
            }
        },
    },
    plugins: [],
}
