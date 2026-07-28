"""Sections 7–22 of the lab report — method, results, UI and conclusions."""

from __future__ import annotations

from build_report import (
    BEST,
    METRICS,
    RANKING,
    SCHEMA,
    add_bullets,
    add_comment,
    add_equation,
    add_figure,
    add_heading,
    add_numbered,
    add_para,
    add_screenshot_slot,
    add_table,
    top_features,
)

import config

money = lambda v: f"${v:,.0f}"


def methodology(doc):
    add_heading(doc, "7. Methodology", level=1)
    add_para(doc, "The complete workflow of the project is shown below.")
    add_figure(doc, "pipeline.png", 1, "End-to-end project workflow")
    add_para(doc,
        "The dataset is first loaded and profiled. It is then split into training and testing "
        "portions, and the training portion is used to fit a preprocessing pipeline together "
        f"with {len(RANKING)} regression models. Each fitted model is evaluated on the unseen "
        "test portion, and the fitted pipelines plus their metrics are written to disk as "
        "artifacts.")
    add_para(doc,
        "At run time the FastAPI backend loads those artifacts once at startup. When a user "
        "submits house characteristics through the React interface, the same input is passed to "
        "every model, and the predictions are returned together with each model's measured "
        "accuracy and displayed in the browser.")
    add_comment(doc,
        "Important design decision worth explaining: training happens offline and the fitted "
        "models are saved. The server never trains on startup, because that delays the port "
        "binding past the hosting platform's health-check timeout and the container is killed.")


def preprocessing(doc):
    add_heading(doc, "8. Data Preprocessing", level=1)
    add_para(doc,
        "Raw data cannot be fed directly to these algorithms: some columns are text, some "
        "contain missing values, and the numeric columns are on wildly different scales — lot "
        "size runs into the tens of thousands while garage capacity is 0–4. Preprocessing is "
        "handled by a scikit-learn ColumnTransformer that routes each column type down its own "
        "path.")
    add_figure(doc, "preprocessing.png", 2, "Preprocessing pipeline: 14 raw columns become 57 model inputs")

    add_heading(doc, "8.1 Handling Missing Values", level=2)
    add_para(doc,
        "The dataset contains 81 missing values, all in GarageType. Numeric columns are imputed "
        "with the median (robust to outliers, unlike the mean) and categorical columns with the "
        "most frequent category.")

    add_heading(doc, "8.2 Feature Scaling", level=2)
    add_para(doc,
        "Numeric features are standardised so that each has zero mean and unit variance:")
    add_equation(doc, "z = (x − μ) / σ",
                 "Equation 15: standardisation. μ and σ are computed on the training set only.")
    add_para(doc,
        "This matters for Linear Regression and is essential for SVR, whose RBF kernel measures "
        "distance between samples — without scaling, LotArea would dominate every distance "
        "calculation simply because its numbers are larger.")
    add_comment(doc,
        "Note that μ and σ come from the TRAINING data only and are then applied unchanged to "
        "the test data and to user input. Computing them over the whole dataset would leak "
        "information from the test set into training.")

    add_heading(doc, "8.3 Categorical Encoding", level=2)
    add_para(doc,
        "Models cannot multiply text, so each categorical column is one-hot encoded: every "
        "possible value becomes its own 0/1 indicator column. Neighborhood alone has 25 levels "
        "and therefore produces 25 indicator columns. Across the 6 categorical columns this "
        "yields 49 indicators, which with the 8 scaled numeric columns gives 57 model inputs.")

    add_heading(doc, "8.4 Train/Test Split", level=2)
    add_para(doc,
        "The dataset is divided 80% training (1,168 records) and 20% testing (292 records) with "
        "a fixed random seed of 42, so results are reproducible. All models share this identical "
        "split, which is what makes the comparison between them fair.")


def model_training(doc):
    add_heading(doc, "9. Model Training", level=1)
    add_para(doc,
        f"Each of the {len(RANKING)} models is wrapped together with the preprocessing steps "
        "into a single scikit-learn Pipeline object. This is significant: the fitted scaler and "
        "encoder are saved inside the model file, so the exact transformations learned during "
        "training are reapplied to any future input automatically.")
    add_para(doc, "The training procedure for each model is:")
    add_numbered(doc, [
        "Fit the preprocessing pipeline on the training data.",
        "Fit the regression model on the transformed training data.",
        "Predict the sale prices of the unseen test records.",
        "Compute MAE, MSE, RMSE and R² from those predictions.",
        "Measure the importance of each feature by permutation.",
        "Save the complete fitted pipeline to disk with compression.",
    ])
    add_para(doc,
        "Saving the whole pipeline rather than only the estimator means the application can "
        "accept raw input such as “Neighborhood = NAmes” with no manual conversion, and removes "
        "any possibility of the training and serving transformations drifting apart.")
    add_screenshot_slot(doc, 1, "Training script output",
        "Run `python train.py` in the terminal and screenshot the output showing each model's "
        "R² and MAE.")


def model_evaluation(doc):
    add_heading(doc, "10. Model Evaluation", level=1)
    add_para(doc,
        "Because this is a regression problem, accuracy in the classification sense does not "
        "apply — a predicted price is essentially never exactly correct. Four standard "
        "regression metrics are used instead.")

    add_heading(doc, "10.1 Mean Absolute Error (MAE)", level=2)
    add_equation(doc, "MAE = (1/n) Σᵢ |yᵢ − ŷᵢ|",
                 "Equation 16: average absolute error, in dollars.")
    add_para(doc,
        "MAE is the average size of the error and is expressed in the same unit as the target, "
        "so it is the easiest metric to explain: an MAE of "
        f"{money(METRICS[BEST]['MAE'])} means the typical prediction is off by about that much. "
        "It treats all errors equally.")

    add_heading(doc, "10.2 Mean Squared Error (MSE)", level=2)
    add_equation(doc, "MSE = (1/n) Σᵢ (yᵢ − ŷᵢ)²",
                 "Equation 17: average squared error, in dollars squared.")
    add_para(doc,
        "Squaring makes MSE punish large errors far more heavily than small ones — an error of "
        "$20,000 counts four times as much as one of $10,000. Its unit is dollars squared, so "
        "the raw value is not directly interpretable.")

    add_heading(doc, "10.3 Root Mean Squared Error (RMSE)", level=2)
    add_equation(doc, "RMSE = √( (1/n) Σᵢ (yᵢ − ŷᵢ)² )",
                 "Equation 18: the square root of MSE, back in dollars.")
    add_para(doc,
        "RMSE keeps MSE's sensitivity to large errors but returns to the original unit. "
        "Comparing RMSE with MAE is informative: RMSE is always the larger of the two, and the "
        "wider the gap, the more the model is making occasional large mistakes.")

    add_heading(doc, "10.4 Coefficient of Determination (R²)", level=2)
    add_equation(doc, "R² = 1 − ( Σᵢ (yᵢ − ŷᵢ)² / Σᵢ (yᵢ − ȳ)² ) = 1 − SS_res/SS_tot",
                 "Equation 19: proportion of variance in the target explained by the model.")
    add_para(doc,
        "R² compares the model against the trivial baseline of always predicting the mean price. "
        "R² = 1 is a perfect fit and R² = 0 means the model is no better than that baseline; a "
        "negative value means it is worse. Unlike the other three metrics it is unitless, which "
        "makes it the natural choice for ranking models.")

    add_heading(doc, "10.5 Results", level=2)
    add_para(doc,
        f"All {len(RANKING)} models were evaluated on the same 292 unseen test records. The "
        "results, ordered by R², are:")
    add_table(doc, ["Rank", "Model", "R²", "MAE", "RMSE", "MSE"],
        [[str(i), name, f"{METRICS[name]['R2']:.4f}", money(METRICS[name]['MAE']),
          money(METRICS[name]['RMSE']), f"{METRICS[name]['MSE']:,.0f}"]
         for i, name in enumerate(RANKING, start=1)],
        widths=[0.5, 1.9, 0.8, 1.0, 1.0, 1.4])
    add_para(doc,
        f"{BEST} achieves the highest R² of {METRICS[BEST]['R2']:.4f}, meaning it explains "
        f"{METRICS[BEST]['R2']*100:.1f}% of the variation in sale price, with a typical error of "
        f"{money(METRICS[BEST]['MAE'])} on a median house price of $163,000 — roughly "
        f"{METRICS[BEST]['MAE']/163000*100:.0f}%.")
    add_comment(doc,
        "Excellent discussion point: the ranking is NOT identical across metrics. Stacking "
        "Ensemble has the lowest MAE while Gradient Boosting has the best R², MSE and RMSE. "
        "This is because MSE and RMSE square the errors and so punish occasional large misses, "
        "whereas MAE weights every error equally. Gradient Boosting makes fewer catastrophic "
        "errors; Stacking has a slightly lower typical error.")
    add_screenshot_slot(doc, 2, "Model comparison tab",
        "Open the app, go to the “Model comparison” tab and capture the four bar charts plus "
        "the metrics table.")


def user_input(doc):
    add_heading(doc, "11. User Input", level=1)
    add_para(doc,
        "The web interface presents one input control per feature, generated automatically from "
        "a schema file written during training rather than hard-coded. Numeric features appear "
        "as sliders bounded by the minimum and maximum values actually present in the dataset, "
        "and categorical features as dropdown lists containing only valid categories. This makes "
        "invalid input impossible to submit.")
    add_table(doc, ["Feature", "Control type", "Allowed values"],
        [[config.FEATURE_LABELS.get(f["name"], f["name"]),
          "Slider" if f["kind"] == "number" else "Dropdown",
          (f"{f['minimum']:g} – {f['maximum']:g}" if f["kind"] == "number"
           else f"{len(f['choices'])} categories")] for f in SCHEMA],
        widths=[2.6, 1.3, 2.4])
    add_screenshot_slot(doc, 3, "Input form",
        "Capture the left-hand panel of the Predict tab showing all 14 input controls.")


def prediction(doc):
    add_heading(doc, "12. Prediction", level=1)
    add_para(doc,
        "When the user submits the form, the values are assembled into a single-row table with "
        f"the same column names used in training and passed to all {len(RANKING)} models. Each "
        "pipeline independently applies its stored preprocessing and produces a price.")
    add_para(doc,
        "The predictions are returned ordered from the most to the least accurate model, and the "
        "headline figure shown to the user is the one from the best-performing model. The "
        "results are colour-coded green through red by model accuracy so the user immediately "
        "knows which number to trust.")
    add_comment(doc,
        "Insert your own values below after running a real prediction — the numbers here are "
        "from the default form values and will differ from yours.")
    add_screenshot_slot(doc, 4, "Prediction results",
        "Enter values in the Predict tab, click Predict, and capture the result card, the "
        "“Prediction by model” chart and the results table.")


def interpretability(doc):
    add_heading(doc, "13. Feature Importance and Interpretability", level=1)
    add_para(doc,
        "A model that predicts well but cannot explain itself is of limited value. This project "
        "measures the contribution of each input feature using permutation importance, which "
        "works by shuffling one column at a time and recording how much the model's R² falls:")
    add_equation(doc, "Importance_j = R²_original − R²_shuffled(j)",
                 "Equation 20: importance of feature j — the accuracy lost when it is scrambled.")
    add_para(doc,
        "Permutation importance was chosen because it is the only technique that works for "
        "every model in the project. Linear Regression exposes coefficients and the tree models "
        "expose Gini importance, but SVR and the two ensembles expose neither — and coefficients "
        "and Gini importance are not comparable to one another in any case. Permutation scores "
        "all models on the same scale.")
    add_para(doc,
        "Importance is measured on the 14 original columns rather than the 57 encoded ones, so "
        "a categorical feature reports a single combined score instead of one per indicator "
        "column.")
    add_para(doc, f"For {BEST}, the most influential features are:")
    add_table(doc, ["Rank", "Feature", "Share of total importance"],
        [[str(i), label, f"{share:.1f}%"]
         for i, (label, share) in enumerate(top_features(BEST, 8), start=1)],
        widths=[0.7, 3.2, 2.2])
    add_para(doc,
        "The result is intuitive and matches domain knowledge: overall build quality and living "
        "area together account for the majority of predictive power, followed by basement area "
        "and garage capacity. Reassuringly, all six models rank the features in a very similar "
        "order, which indicates the pattern is genuinely present in the data rather than an "
        "artefact of one algorithm.")
    add_screenshot_slot(doc, 5, "Feature importance tab",
        "Open the “Feature importance” tab and capture both charts for the best model.")


def user_interface(doc):
    add_heading(doc, "14. User Interface", level=1)
    add_para(doc,
        "The application is a web interface built with React and Vite, communicating with a "
        "FastAPI backend over a JSON API. It is organised into five tabs.")

    add_heading(doc, "14.1 Predict Tab", level=2)
    add_bullets(doc, [
        "14 input controls generated from the training schema",
        "Headline predicted price from the best model",
        "Bar chart comparing all models' predictions for the current input",
        "Table of every model's prediction with its accuracy",
    ])

    add_heading(doc, "14.2 Model Comparison Tab", level=2)
    add_bullets(doc, [
        "Four bar charts, one per metric, ranked best to worst",
        "Percentage gap to the winning model on every bar",
        "Metrics table with each column coloured by its own ranking",
    ])

    add_heading(doc, "14.3 Feature Importance Tab", level=2)
    add_bullets(doc, [
        "Permutation importance for any selected model",
        "A second chart excluding the dominant feature so the rest are readable",
    ])

    add_heading(doc, "14.4 Diagnostics Tab", level=2)
    add_bullets(doc, [
        "Actual vs predicted scatter plot with a perfect-fit reference line",
        "Residual histogram with mean and standard deviation",
    ])

    add_heading(doc, "14.5 EDA Tab", level=2)
    add_bullets(doc, [
        "The full ydata-profiling report embedded in the application",
        "Distributions, missing values, correlations, interactions and alerts",
    ])

    add_screenshot_slot(doc, 6, "Full application interface",
        "Capture the whole browser window showing the app with the tab bar visible.")


def visualization(doc):
    add_heading(doc, "15. Visualization", level=1)
    add_para(doc,
        "All charts follow one consistent convention: models are always sorted best to worst and "
        "coloured on a green-to-red scale, so the reader can identify the winner at a glance "
        "without reading any numbers. Colour is never the only cue — every bar also carries a "
        "value label, and every chart has a table equivalent.")

    add_heading(doc, "15.1 Metric Comparison Charts", level=2)
    add_para(doc,
        "Four horizontal bar charts compare MAE, MSE, RMSE and R² across all models. Each bar is "
        "labelled with its value and its percentage gap to the best model, which matters because "
        "the raw differences are small enough that the bars alone look similar.")

    add_heading(doc, "15.2 Prediction Comparison", level=2)
    add_para(doc,
        "A bar chart shows what each model predicts for the current user input, ordered by model "
        "accuracy, with a dashed line marking the average across all models. This updates every "
        "time the user changes an input.")

    add_heading(doc, "15.3 Feature Importance Charts", level=2)
    add_para(doc,
        "Two horizontal bar charts show permutation importance. The first shows all 14 features "
        "honestly on one scale; the second removes the dominant feature and rescales, because "
        "otherwise the smaller contributors would be invisible.")

    add_heading(doc, "15.4 Actual vs Predicted Scatter", level=2)
    add_para(doc,
        "Each test house is plotted with its true price on the x-axis and the predicted price on "
        "the y-axis, against a dashed diagonal representing perfect prediction. Points above the "
        "line are over-predictions and points below are under-predictions. Systematic curvature "
        "or fanning would indicate a problem with the model.")

    add_heading(doc, "15.5 Residual Histogram", level=2)
    add_para(doc,
        "The distribution of prediction errors. A good model produces a symmetric bell shape "
        "centred on zero — a shift away from zero would indicate systematic bias, and two peaks "
        "would suggest two distinct populations mixed together.")

    add_heading(doc, "15.6 Exploratory Data Analysis", level=2)
    add_para(doc,
        "An automated profiling report generated with ydata-profiling before any modelling, "
        "covering per-column distributions, missing values, correlation matrices, feature "
        "interactions and automatically raised data-quality alerts.")

    add_screenshot_slot(doc, 7, "Diagnostics tab",
        "Capture the actual-vs-predicted scatter and the residual histogram side by side.")
    add_screenshot_slot(doc, 8, "EDA report",
        "Open the EDA tab and capture the profiling report overview showing dataset statistics "
        "and variable types.")


def sample_output(doc):
    add_heading(doc, "16. Sample Output", level=1)
    add_para(doc, "A representative input and the resulting output are shown below.")
    add_comment(doc,
        "Replace this entire table with your own run. Enter values in the app, click Predict, "
        "and copy the numbers from the results table.")

    add_heading(doc, "16.1 Input", level=2)
    add_table(doc, ["Feature", "Value"],
        [[config.FEATURE_LABELS.get(f["name"], f["name"]),
          str(f["default"])] for f in SCHEMA],
        widths=[3.4, 2.9])

    add_heading(doc, "16.2 Model Predictions", level=2)
    add_table(doc, ["Rank", "Model", "Predicted Price", "Model R²"],
        [[str(i), name, "[your value]", f"{METRICS[name]['R2']:.4f}"]
         for i, name in enumerate(RANKING, start=1)],
        widths=[0.6, 2.3, 1.7, 1.4])

    add_heading(doc, "16.3 Summary", level=2)
    add_bullets(doc, [
        f"Best performing model: {BEST}",
        "Headline prediction: [your value]",
        "Average across all models: [your value]",
        f"Expected typical error: ±{money(METRICS[BEST]['MAE'])} (the best model's MAE)",
    ])


def deployment(doc):
    add_heading(doc, "17. Deployment", level=1)
    add_para(doc,
        "The application is split into two independently deployed halves, which is standard "
        "practice for web applications and allows each to be hosted on infrastructure suited "
        "to it.")
    add_table(doc, ["Component", "Technology", "Platform", "Role"], [
        ["Backend", "FastAPI + Uvicorn", "Render", "Loads models, serves the JSON API"],
        ["Frontend", "React + Vite", "Vercel", "Static site delivered by CDN"],
        ["Source", "Git", "GitHub", "Version control for both"],
    ], widths=[1.2, 1.6, 1.1, 2.4])
    add_para(doc,
        "The trained model files are committed to the repository so the server loads them "
        "directly at startup. Training on startup instead would delay the server binding its "
        "port past the hosting platform's health-check window, causing the deployment to be "
        "terminated.")
    add_comment(doc,
        "Add your live URLs here once deployed — e.g. Frontend: https://your-app.vercel.app, "
        "Backend: https://your-api.onrender.com")
    add_screenshot_slot(doc, 9, "Deployed application",
        "Open your deployed Vercel URL in a browser and capture the page with the URL bar "
        "visible, to prove it is live.")


def advantages(doc):
    add_heading(doc, "18. Advantages", level=1)
    add_numbered(doc, [
        f"{len(RANKING)} regression algorithms can be compared directly on identical data.",
        "Four complementary evaluation metrics are reported rather than a single number.",
        "Predictions are produced in real time through an interactive web interface.",
        "The best-performing model is identified automatically.",
        "Feature importance explains why the models predict what they do.",
        "Diagnostic plots reveal how the models fail, not merely how often.",
        "The preprocessing pipeline is stored with each model, preventing train/serve mismatch.",
        "Input controls are generated from the data, so invalid values cannot be entered.",
        "Automated EDA documents the dataset before any modelling decision is taken.",
        "The application is deployed publicly and accessible from any browser.",
    ])


def limitations(doc):
    add_heading(doc, "19. Limitations", level=1)
    add_numbered(doc, [
        "The dataset covers a single city (Ames, Iowa) over a limited period, so the models "
        "would not transfer to another housing market.",
        "Only 14 of the 81 available columns are used, so some predictive information is "
        "discarded for the sake of a usable form.",
        "Evaluation rests on a single train/test split rather than repeated cross-validation.",
        "Hyper-parameters are left at their library defaults and were not tuned.",
        "The models under-predict the most expensive houses, a form of regression to the mean.",
        "1,460 records is a small dataset by modern standards, particularly at the price extremes.",
        "No prediction interval is reported, only a point estimate.",
        "The application is intended for educational demonstration, not for property valuation.",
    ])
    add_comment(doc,
        "The regression-to-the-mean point is worth expanding if you have space: the models only "
        "ever predict within roughly the middle of the observed price range, because tree-based "
        "models predict by averaging training examples and extreme prices are rare.")


def future_work(doc):
    add_heading(doc, "20. Future Improvements", level=1)
    add_bullets(doc, [
        "Tune hyper-parameters using GridSearchCV or RandomizedSearchCV.",
        "Replace the single split with k-fold cross-validation for more reliable estimates.",
        "Add gradient boosting libraries such as XGBoost, LightGBM or CatBoost.",
        "Engineer new features such as house age at sale or total square footage.",
        "Report prediction intervals instead of single point estimates using quantile regression.",
        "Apply SHAP values for per-prediction explanations rather than global importance.",
        "Allow users to upload their own dataset and retrain from the interface.",
        "Add a classification section to the same application for comparison.",
        "Log a history of predictions and allow the results to be downloaded.",
        "Address the under-prediction of expensive houses with target transformation or "
        "sample weighting.",
    ])


def result(doc):
    add_heading(doc, "21. Result", level=1)
    add_para(doc,
        f"The project successfully trains and compares {len(RANKING)} regression models on the "
        "Ames Housing dataset. The developed application allows a user to:")
    add_bullets(doc, [
        "Enter the characteristics of a house through an interactive form.",
        f"Generate a price prediction from all {len(RANKING)} models simultaneously.",
        "View each model's prediction alongside its measured accuracy.",
        "Compare the models on MAE, MSE, RMSE and R².",
        "Identify the best-performing model automatically.",
        "Examine which features drive each model's predictions.",
        "Inspect residual and actual-vs-predicted diagnostics.",
        "Explore the dataset through an automated profiling report.",
    ])
    add_para(doc,
        f"The best-performing model, {BEST}, achieved an R² of {METRICS[BEST]['R2']:.4f} with a "
        f"mean absolute error of {money(METRICS[BEST]['MAE'])} on unseen data. The two ensemble "
        "methods performed comparably, while Linear Regression and Support Vector Regression "
        "trailed by roughly five percentage points of R², confirming that the relationship "
        "between house characteristics and price is non-linear.")


def conclusion(doc):
    add_heading(doc, "22. Conclusion", level=1)
    add_para(doc,
        f"In this project a multiple-model regression system was developed using the Ames "
        f"Housing dataset. {len(RANKING)} algorithms — Linear Regression, Random Forest, "
        "Gradient Boosting, Support Vector Regression, a Voting Ensemble and a Stacking "
        "Ensemble — were trained on identical data and compared using four standard metrics.")
    add_para(doc,
        "The work demonstrates that algorithm choice matters: the tree-based ensembles clearly "
        "outperformed the linear and kernel methods, indicating that price depends on its "
        "drivers non-linearly and through interactions between them. It also demonstrates that "
        "correct preprocessing is not optional — Support Vector Regression produced a negative "
        "R², worse than predicting the mean, until its target variable was scaled.")
    add_para(doc,
        "Beyond raw accuracy, the project shows the value of interpretation and diagnostics. "
        "Permutation importance revealed that overall quality and living area dominate the "
        "prediction, and the residual analysis exposed a systematic tendency to under-predict "
        "expensive houses that no single accuracy score would have shown.")
    add_para(doc,
        "Overall the project provides practical experience of the complete machine learning "
        "workflow: exploratory data analysis, preprocessing, model training, evaluation, "
        "interpretation, interface development and public deployment.")
