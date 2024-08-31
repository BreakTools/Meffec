import React from "react";
import { Text, StyleSheet, View } from "react-native";
import EffectDisplay from "./EffectDisplay";

interface EffectProps {
    category: string;
    name: string;
    description: string;
}

interface CategoryDisplayProps {
    name: string;
    effects: Array<EffectProps>;
    openCollectionEditor: (
        category: string,
        name: string,
        description: string
    ) => void;
}

export default function CategoryDisplay({
    name,
    effects,
    openCollectionEditor,
}: CategoryDisplayProps) {
    return (
        <View>
            <Text style={styles.categoryText}>{name}</Text>
            <View style={styles.effectsContainer}>
                {effects.map((effect, index) => (
                    <View key={index} style={styles.effectItem}>
                        <EffectDisplay
                            category={name}
                            name={effect.name}
                            description={effect.description}
                            openCollectionEditor={openCollectionEditor}
                        />
                    </View>
                ))}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    categoryText: {
        color: "#FFFFFF",
        fontSize: 20,
        fontWeight: "500",
        marginTop: 10,
        marginBottom: 8,
        fontFamily: "Inter",
    },
    effectsContainer: {
        flexDirection: "row",
        flexWrap: "wrap",
        justifyContent: "space-between",
        marginBottom: 15,
    },
    effectItem: {
        width: "48%",
    },
});
