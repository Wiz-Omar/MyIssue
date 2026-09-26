import { Button } from "@/components/ui/button";
import { Link } from "react-router";

export default function DashboardPage() {
    return (
        <div>
            Dashboard content
            <Button>
                <Link to="/login">Test</Link>
            </Button>
        </div>
    )
}