import { WebSocketContext } from "@/websockets/WebSocketContext";
import React, { useContext } from "react";
import { Text, StyleSheet, View, TouchableOpacity, Image } from "react-native";

interface CollectedEffectDisplayProps {
    category: string;
    name: string;
    description: string;
}

export default function CollectedEffectDisplay({
    category,
    name,
    description,
}: CollectedEffectDisplayProps) {
    const websocketContext = useContext(WebSocketContext);

    function playEffect(category: string, name: string) {
        websocketContext?.sendMessage(
            JSON.stringify({
                type: "play_effect",
                data: {
                    category: category,
                    name: name,
                },
            })
        );
    }

    return (
        <View style={styles.effectContainer}>
            <TouchableOpacity onPress={() => playEffect(category, name)}>
                <Text style={styles.categoryText}>
                    {">"}
                    {category}
                </Text>
                <Text style={styles.nameText}>{name}</Text>
                <Text style={styles.descriptionText}>{description}</Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    effectContainer: {
        backgroundColor: "#1C1C1C",
        borderWidth: 0.2,
        borderColor: "#FFFFFF",
        borderRadius: 8,
        padding: 8,
        shadowColor: "#FFFFFF",
        shadowOpacity: 0.3,
        shadowRadius: 4,
        shadowOffset: {
            width: 0,
            height: 0,
        },
        elevation: 2,
        marginBottom: 15,
    },
    nameText: {
        color: "#FFFFFF",
        fontSize: 14,
        fontWeight: "500",
        fontFamily: "Inter",
        marginBottom: 2,
        width: "80%",
    },
    descriptionText: {
        color: "#FFFFFF",
        fontSize: 10,
        fontWeight: "400",
        fontFamily: "Inter",
    },
    categoryText: {
        color: "#DFDFDF",
        fontSize: 12,
        fontWeight: "200",
        fontFamily: "Inter",
        marginBottom: 1,
    },
});
