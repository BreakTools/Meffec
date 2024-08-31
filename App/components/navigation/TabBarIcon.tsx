import { Image, ImageSourcePropType, StyleSheet } from "react-native";

type TabBarIconProps = {
    iconFile: ImageSourcePropType;
    focused: boolean;
};
export function TabBarIcon({ iconFile, focused }: TabBarIconProps) {
    const opacity = focused ? 1 : 0.6;
    return <Image source={iconFile} style={[styles.icon, { opacity }]} />;
}

const styles = StyleSheet.create({
    icon: {
        width: 26,
        height: 26,
    },
});
