import React from "react";
import { Text, StyleSheet, TouchableOpacity, Image } from "react-native";

interface CollectionDisplayProps {
    collectionName: string;
    allCollections: any;
    category: string;
    name: string;
    configureCollection: (
        collectionName: string,
        action: "add" | "remove"
    ) => void;
    removeCollection: (collectionName: string) => void;
}

export default function CollectionDisplay({
    collectionName,
    allCollections,
    category,
    name,
    configureCollection,
    removeCollection,
}: CollectionDisplayProps) {
    var enabled = false;

    if (allCollections.hasOwnProperty(collectionName)) {
        const effectExists = allCollections[collectionName].some(
            (effect: { category: string; name: string }) =>
                effect.category === category && effect.name === name
        );

        enabled = effectExists ? true : false;
    }

    function toggleEnabled() {
        if (enabled) {
            configureCollection(collectionName, "remove");
        } else {
            configureCollection(collectionName, "add");
        }
    }

    return (
        <TouchableOpacity
            style={[
                styles.collectionContainer,
                enabled
                    ? styles.enabledCollectionContainer
                    : styles.disabledCollectionContainer,
            ]}
            onPress={toggleEnabled}
        >
            <TouchableOpacity
                style={styles.deleteImageContainer}
                onPress={() => removeCollection(collectionName)}
            >
                <Image
                    source={require("@/assets/icons/delete.png")}
                    style={styles.deleteImage}
                ></Image>
            </TouchableOpacity>

            <Text style={enabled ? styles.enabledText : styles.disabledText}>
                {collectionName}
            </Text>
        </TouchableOpacity>
    );
}

const styles = StyleSheet.create({
    collectionContainer: {
        alignItems: "center",
        borderWidth: 0.2,
        borderColor: "#838383",
        borderRadius: 8,
        padding: 6,
        shadowColor: "#FFFFFF",
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
        marginBottom: 10,
        marginHorizontal: 4,
    },
    disabledCollectionContainer: {},
    enabledCollectionContainer: {
        backgroundColor: "#FFFFFF",
    },
    disabledText: {
        color: "#FFFFFF",
        fontSize: 14,
        fontWeight: "300",
        fontFamily: "Inter",
        marginHorizontal: 10,
        textAlign: "center",
        alignContent: "center",
    },
    enabledText: {
        color: "#000000",
        fontSize: 14,
        fontWeight: "300",
        fontFamily: "Inter",
        marginHorizontal: 10,
        textAlign: "center",
    },
    deleteImage: {
        width: 15,
        height: 15,
        transform: "translate(10px, -10px)",
    },
    deleteImageContainer: {
        marginBottom: -15,
        alignSelf: "flex-end",
    },
});
