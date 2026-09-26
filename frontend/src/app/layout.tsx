import { 
    Sidebar, 
    SidebarInset, 
    SidebarProvider,
    SidebarTrigger,
    SidebarContent,
    SidebarGroup, 
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton }
from "@/components/ui/sidebar.tsx"
import { Bug, LayoutDashboard } from 'lucide-react'
import { Outlet } from 'react-router'

export default function AppLayout(){
    return (
        <SidebarProvider>
            <Sidebar collapsible='icon' side='left'>
                <SidebarContent>
                    <SidebarGroup>
                        <SidebarMenu>
                            <SidebarMenuItem>
                                <SidebarMenuButton tooltip="Dashboard">
                                    <LayoutDashboard />
                                    <span>Dashboard</span>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                            <SidebarMenuItem>
                                <SidebarMenuButton tooltip="Issues">
                                    <Bug />
                                    <span>Issues</span>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        </SidebarMenu>
                    </SidebarGroup>
                </SidebarContent>
            </Sidebar>

            <SidebarInset>
                <header className="flex items-center border-b p-2">
                    <SidebarTrigger />
                </header>
                <main className="p-4">
                    <Outlet />
                </main>
            </SidebarInset>
        </SidebarProvider>
    )
}