const text = `{

"plan_title": "Indian Vegetarian Fitness Plan",

"daily_total_calories": 2470,

"daily_total_protein_g": 103,

"meals": [

{

"meal_type": "Breakfast",

"items": [

{

"name": "Besan Cheela (Gram Flour Pancakes)",

"portion": "2 medium",

"calories": 380,

"protein_g": 18

},

{

"name": "Milk",

"portion": "200 ml",

"calories": 120,

"protein_g": 6

}

],

"total_calories": 500,

"total_protein_g": 24

},

{

"meal_type": "Lunch",

"items": [

{

"name": "Rajma Curry (Kidney Bean Gravy)",

"portion": "1 large serving (made with 70g dry rajma)",

"calories": 315,

"protein_g": 18

},

{

"name": "Brown Rice",

"portion": "1.5 cups cooked (from 140g raw rice)",

"calories": 505,

"protein_g": 9

},

{

"name": "Cucumber and Tomato Salad",

"portion": "1 medium bowl",

"calories": 10,

"protein_g": 1

}

],

"total_calories": 830,

"total_protein_g": 28

},

{

"meal_type": "Snack",

"items": [

{

"name": "Roasted Chana (Black Chickpeas)",

"portion": "80g",

"calories": 290,

"protein_g": 16

},

{

"name": "Apple",

"portion": "1 medium",

"calories": 95,

"protein_g": 1

}

],

"total_calories": 385,

"total_protein_g": 17

},

{

"meal_type": "Dinner",

"items": [

{

"name": "Dal Tadka (Lentil Soup)",

"portion": "1 serving (made with 70g dry lentils)",

"calories": 290,

"protein_g": 18

},

{

"name": "Whole Wheat Roti",

"portion": "3 medium",

"calories": 330,

"protein_g": 12

},

{

"name": "Mixed Vegetable Sabzi",

"portion": "1 serving (made with 180g mixed veggies)",

"calories": 135,

"protein_g": 4

}

],

"total_calories": 755,

"total_protein_g": 34

}

]

}`;
try {
  JSON.parse(text);
  console.log("SUCCESS");
} catch (e) {
  console.log("FAILED", e);
}
