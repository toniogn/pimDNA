import { Box, Button, Container, Typography } from "@mui/material";
import { useTranslate } from "@refinedev/core";
import { ThemedTitleV2 } from "@refinedev/mui";

import { useAuth0 } from "@auth0/auth0-react";

import { AppIcon } from "../components/app-icon";

export const Login: React.FC = () => {
  const { loginWithRedirect } = useAuth0();

  const t = useTranslate();

  return (
    <Container
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Box
        display="flex"
        gap="36px"
        justifyContent="center"
        flexDirection="column"
      >
        <ThemedTitleV2
          collapsed={false}
          wrapperStyles={{
            fontSize: "22px",
            justifyContent: "center",
          }}
          text="peace in our DNA"
          icon={<AppIcon />}
        />

        <Button
          style={{ width: "240px" }}
          size="large"
          variant="contained"
          onClick={() => loginWithRedirect()}
        >
          {t("pages.login.signin", "Sign in")}
        </Button>
        <Typography align="center" color={"text.secondary"} fontSize="12px">
          Powered by
          <img
            style={{ padding: "0 5px" }}
            alt="Auth0"
            src="https://refine.ams3.cdn.digitaloceanspaces.com/superplate-auth-icons%2Fauth0-2.svg"
          />
          Auth0
        </Typography>
      </Box>
    </Container>
  );
};
