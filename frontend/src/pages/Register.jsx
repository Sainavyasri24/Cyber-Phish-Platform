import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";

function Register() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        try {
            await axios.post("http://127.0.0.1:8000/register", {
                username,
                password
            });
            alert("Registration successful! Please login.");
            navigate("/login");
        } catch (err) {
            setError("Registration failed. Username might be taken.");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-black text-white font-sans">
            <div className="w-full max-w-md p-8 border border-gray-800 rounded-sm bg-[#0a0a0a]">
                <h2 className="text-3xl font-serif font-bold mb-6 text-center">Create Account</h2>

                {error && <p className="text-red-500 text-sm mb-4 text-center">{error}</p>}

                <form onSubmit={handleRegister} className="space-y-6">
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Username</label>
                        <input
                            type="text"
                            required
                            className="w-full bg-black border border-gray-700 p-2 text-white focus:border-purple-500 outline-none rounded-sm"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Password</label>
                        <input
                            type="password"
                            required
                            className="w-full bg-black border border-gray-700 p-2 text-white focus:border-purple-500 outline-none rounded-sm"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Confirm Password</label>
                        <input
                            type="password"
                            required
                            className="w-full bg-black border border-gray-700 p-2 text-white focus:border-purple-500 outline-none rounded-sm"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                    </div>

                    <button type="submit" className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 rounded-sm transition-colors">
                        Register
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-500">
                    Already have an account? <Link to="/login" className="text-purple-400 hover:text-purple-300">Login</Link>
                </p>
            </div>
        </div>
    );
}

export default Register;
