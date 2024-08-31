import React from "react";
import { Text, StyleSheet } from "react-native";

interface BigScreenTextProps {
    text: string;
}

export default function BigScreenText({ text }: BigScreenTextProps) {
    return <Text style={styles.text}>{text}</Text>;
}

const styles = StyleSheet.create({
    text: {
        color: "#FFFFFF",
        fontSize: 42,
        fontWeight: "500",
        marginTop: 4,
        fontFamily: "Inter",
        marginHorizontal: 20,
    },
});
