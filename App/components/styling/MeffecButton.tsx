import React from "react";
import { Text, StyleSheet, View } from "react-native";

interface MeffecButton {
    text: string;
}

export default function MeffecButton({ text }: MeffecButton) {
    return (
        <View style={styles.buttonContainer}>
            <Text style={styles.text}>{text}</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    buttonContainer: {
        alignItems: "center",
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
    text: {
        color: "#FFFFFF",
        fontSize: 14,
        fontWeight: "300",
        fontFamily: "Inter",
        marginHorizontal: 10,
    },
});
