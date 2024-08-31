import { WebSocketContext } from "@/websockets/WebSocketContext";
import React, { useContext } from "react";
import { Text, StyleSheet, View, TouchableOpacity, Image } from "react-native";

interface EffectDisplayProps {
    category: string;
    name: string;
    description: string;
    openCollectionEditor: (
        category: string,
        name: string,
        description: string
    ) => void;
}

export default function EffectDisplay({
    category,
    name,
    description,
    openCollectionEditor,
}: EffectDisplayProps) {
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
                <View style={styles.nameIconContainer}>
                    <Text style={styles.nameText}>{name}</Text>
                    <TouchableOpacity
                        onPress={() =>
                            openCollectionEditor(category, name, description)
                        }
                    >
                        <Image
                            source={require("@/assets/icons/add-to-collection.png")}
                            style={styles.icon}
                        />
                    </TouchableOpacity>
                </View>

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
        padding: 6,
        shadowColor: "#FFFFFF",
        shadowOpacity: 0.3,
        shadowRadius: 4,
        shadowOffset: {
            width: 0,
            height: 0,
        },
        elevation: 2,
        marginBottom: 10,
    },
    nameIconContainer: {
        flexDirection: "row",
        justifyContent: "space-between",
    },
    icon: {
        width: 20,
        height: 20,
    },
    nameText: {
        color: "#FFFFFF",
        fontSize: 14,
        fontWeight: "500",
        fontFamily: "Inter",
        marginBottom: 4,
        width: "80%",
    },
    descriptionText: {
        color: "#FFFFFF",
        fontSize: 10,
        fontWeight: "300",
        fontFamily: "Inter",
    },
});
