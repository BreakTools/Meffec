import { WebSocketContext } from "@/websockets/WebSocketContext";
import React, { useContext } from "react";
import { StyleSheet, View, Text } from "react-native";

export default function WebSocketConnectionOverlay({ children }: any) {
    const websocketContext = useContext(WebSocketContext);

    if (!websocketContext?.connected) {
        return (
            <View style={styles.container}>
                <Text style={styles.text}>
                    Not connected to server. Reconnecting in{" "}
                    {websocketContext?.reconnectionDisplayCountdown}....
                </Text>
                {children}
            </View>
        );
    }

    return <View style={styles.container}>{children}</View>;
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    text: {
        color: "#FFFFFF",
        fontSize: 16,
        fontWeight: "bold",
        backgroundColor: "#FF0000",
        padding: 10,
    },
});
