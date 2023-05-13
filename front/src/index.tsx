import { Auth0Provider } from "@auth0/auth0-react";
import React from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import "./i18n";

const container = document.getElementById("root") as HTMLElement;
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <React.Suspense fallback="loading">
      <Auth0Provider
        domain="dev-qg1ftdys736bk5i3.us.auth0.com"
        clientId="Be5vsLunFvpzPf4xfXtaMxrZUVBjjNPO"
        redirectUri={window.location.origin}
      >
        <App />
      </Auth0Provider>
    </React.Suspense>
  </React.StrictMode>
);
