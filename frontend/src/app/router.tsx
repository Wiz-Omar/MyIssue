import { createBrowserRouter } from "react-router";
import AppLayout from "./layout";
import LoginPage from "@/routes/login";
import DashboardPage from "@/routes/dashboard";
import IssueListPage from "@/routes/issues/issues";
import UsersPage from "@/routes/admin/users";
import { RequireAuth } from "./require-auth";

export const router = createBrowserRouter([
    { path: "/login", element: <LoginPage /> },
    {
        path: "/",
        element: <RequireAuth> <AppLayout /> </RequireAuth>,
        children: [
            { index: true, element: <DashboardPage /> },
            { path: "issues", element: <IssueListPage /> },
            { path: "admin/users", element: <UsersPage /> },
        ],
    },
]);