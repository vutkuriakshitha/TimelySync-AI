import { render, screen } from "@testing-library/react";
import App from "./App";

// The app requires a valid backend session to reach any protected page, so an
// unauthenticated render should always redirect to the public login form
// rather than crashing with a white screen.
test("renders the login page when no user is authenticated", async () => {
  render(<App />);
  const heading = await screen.findByRole("heading", { name: /sign in/i });
  expect(heading).toBeInTheDocument();
});
