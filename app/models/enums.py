from enum import Enum


class UserRole(str, Enum):
    STANDARD = "standard"
    WELLNESS_CREATOR = "wellness_creator"
    MODERATOR = "moderator"
    ADMIN = "admin"


class EatingStyle(str, Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    OTHER = "other"


class FitnessInterest(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    CARDIO = "cardio"
    STRENGTH_TRAINING = "strength_training"
    YOGA = "yoga"
    RUNNING = "running"
    CYCLING = "cycling"
    HOME_WORKOUTS = "home_workouts"
    OTHER = "other"


class FastingPreference(str, Enum):
    NONE = "none"
    INTERMITTENT_16_8 = "intermittent_16_8"
    INTERMITTENT_18_6 = "intermittent_18_6"
    OMAD = "omad"
    ALTERNATE_DAY = "alternate_day"
    RELIGIOUS = "religious"
    OTHER = "other"


class PostCategory(str, Enum):
    NUTRITION = "nutrition"
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    VEGAN = "vegan"
    FASTING = "fasting"
    HYDRATION = "hydration"
    MENTAL_WELLNESS = "mental_wellness"
    SLEEP_HABITS = "sleep_habits"
    HOME_WORKOUTS = "home_workouts"
    CARDIO = "cardio"
    TRADITIONAL_MEDICINE = "traditional_medicine"
    HERBAL_PLANTS = "herbal_plants"
    HEALTHY_DRINKS = "healthy_drinks"


class HabitType(str, Enum):
    EATING = "eating"
    WATER_INTAKE = "water_intake"
    SLEEP = "sleep"
    WALKING = "walking"
    GYM = "gym"
    RUNNING = "running"
    MEDITATION = "meditation"
    FASTING = "fasting"
    RESTING = "resting"
    STRETCHING = "stretching"
    VITAMIN_INTAKE = "vitamin_intake"


class GroupPrivacy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class MealCategory(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    KETO = "keto"
    VEGAN = "vegan"
    HIGH_PROTEIN = "high_protein"
    DIABETIC_FRIENDLY = "diabetic_friendly"
    LOW_CARB = "low_carb"
    AFRICAN = "african"
    MEDITERRANEAN = "mediterranean"
    HEALTHY_SNACKS = "healthy_snacks"


class WorkoutLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseCategory(str, Enum):
    CARDIO = "cardio"
    STRENGTH_TRAINING = "strength_training"
    YOGA = "yoga"
    STRETCHING = "stretching"
    MOBILITY = "mobility"
    HIIT = "hiit"
    RUNNING = "running"
    CYCLING = "cycling"
    DANCE_FITNESS = "dance_fitness"
