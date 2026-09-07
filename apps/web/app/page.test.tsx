import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "./page";

describe("home page", () => {
  it("states the prototype scope and workflow", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("SEE THE");
    expect(screen.getByText(/synthetic or cleared public reports/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /reviewer stays in control/i })).toBeInTheDocument();
  });
});
