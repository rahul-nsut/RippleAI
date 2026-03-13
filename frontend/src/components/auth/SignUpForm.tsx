"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import { apiRequestHelper } from "@/lib/api";

export default function SignUpForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
        const res = await apiRequestHelper("/auth/signup", {
            method: "POST",
            body: JSON.stringify({ full_name: name, email, password }),
        });
        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Signup failed");
            return;
        }
        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("email", email);
        localStorage.setItem("full_name", data.full_name);
        router.push("/dashboard");
    } catch (err) {
        console.error("Error signing up:", err);
        alert("Failed to sign up");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4"
    >
      <Input
        label="Name"
        type="text"
        placeholder="Your Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <Input
        label="Email"
        type="email"
        placeholder="your-name@company.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <Input
        label="Password"
        type="password"
        placeholder="********"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <Button type="submit">
        Sign Up
      </Button>
    </form>
  );
}
