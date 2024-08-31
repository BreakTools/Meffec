import { Tabs } from "expo-router";
import React from "react";

import { TabBarIcon } from "@/components/navigation/TabBarIcon";

export default function TabLayout() {
    return (
        <Tabs
            screenOptions={{
                tabBarActiveTintColor: "#FFFFFF",
                tabBarInactiveTintColor: "#DEDEDE",
                tabBarStyle: {
                    backgroundColor: "#1C1C1C",
                    borderTopWidth: 0,
                },
                headerShown: false,
            }}
        >
            <Tabs.Screen
                name="collections"
                options={{
                    title: "Collections",
                    tabBarIcon: ({ color, focused }) => (
                        <TabBarIcon
                            iconFile={require("@/assets/icons/collections.png")}
                            focused={focused}
                        />
                    ),
                }}
            />
            <Tabs.Screen
                name="effects"
                options={{
                    title: "Effects",
                    tabBarIcon: ({ color, focused }) => (
                        <TabBarIcon
                            iconFile={require("@/assets/icons/effects.png")}
                            focused={focused}
                        />
                    ),
                }}
            />
            <Tabs.Screen
                name="settings"
                options={{
                    title: "Settings",
                    tabBarIcon: ({ color, focused }) => (
                        <TabBarIcon
                            iconFile={require("@/assets/icons/settings.png")}
                            focused={focused}
                        />
                    ),
                }}
            />
        </Tabs>
    );
}
