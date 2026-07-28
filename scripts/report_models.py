"""Section 6 of the lab report — the algorithms and their mathematics.

Equations are plain Unicode text in a Cambria Math run so they remain editable
in Word; python-docx cannot emit native OMML equation objects.
"""

from __future__ import annotations

from build_report import (
    RANKING,
    add_comment,
    add_equation,
    add_heading,
    add_para,
    add_table,
)


def models_used(doc):
    add_heading(doc, "6. Machine Learning Models Used", level=1)
    add_para(doc,
        f"{len(RANKING)} regression algorithms were trained. Each receives exactly the same "
        "preprocessed inputs and is evaluated on exactly the same test split, so any difference "
        "in score is attributable to the algorithm alone.")
    add_para(doc,
        "Throughout this section n is the number of training samples, p the number of input "
        "features, xᵢ the feature vector of sample i, yᵢ its true sale price and ŷᵢ the "
        "predicted price.")

    # --- 6.1 Linear Regression ---
    add_heading(doc, "6.1 Linear Regression", level=2)
    add_para(doc,
        "Linear Regression is the simplest of the algorithms used. It assumes the target is a "
        "weighted sum of the input features plus a constant, and learns one weight per feature.")
    add_equation(doc, "ŷ = β₀ + β₁x₁ + β₂x₂ + ⋯ + βₚxₚ",
                 "Equation 1: the linear model. β₀ is the intercept; βⱼ is the weight of feature j.")
    add_para(doc,
        "The weights are chosen to minimise the Residual Sum of Squares — the total squared "
        "difference between true and predicted values:")
    add_equation(doc, "RSS(β) = Σᵢ (yᵢ − ŷᵢ)² = Σᵢ (yᵢ − βᵀxᵢ)²",
                 "Equation 2: the ordinary least squares objective.")
    add_para(doc,
        "Setting the derivative of Equation 2 to zero gives a closed-form solution, the normal "
        "equation — no iterative training is required:")
    add_equation(doc, "β̂ = (XᵀX)⁻¹ Xᵀy",
                 "Equation 3: the normal equation. X is the n×p design matrix of inputs.")
    add_para(doc,
        "Strength: fast to fit, and every weight is directly interpretable as the change in "
        "price per unit change in that feature. Weakness: it can only express straight-line "
        "relationships, so it cannot capture effects such as quality mattering more for large "
        "houses than for small ones.")

    # --- 6.2 Random Forest ---
    add_heading(doc, "6.2 Random Forest", level=2)
    add_para(doc,
        "Random Forest is an ensemble of Decision Trees. A decision tree splits the data "
        "repeatedly on feature thresholds; for regression each split is chosen to minimise the "
        "variance of the target within the two resulting groups:")
    add_equation(doc, "Loss(split) = (n_L/n)·MSE(L) + (n_R/n)·MSE(R)",
                 "Equation 4: weighted impurity of a candidate split into left (L) and right (R) groups.")
    add_para(doc,
        "A single deep tree memorises its training data and generalises poorly. Random Forest "
        "reduces this by training B trees, each on a bootstrap resample of the rows and "
        "considering only a random subset of features at each split, then averaging them:")
    add_equation(doc, "ŷ = (1/B) Σ_{b=1..B} T_b(x)",
                 "Equation 5: the forest prediction is the mean of its B trees. Here B = 100.")
    add_para(doc,
        "Because the trees are decorrelated, their individual errors partly cancel when averaged. "
        "This is variance reduction: were the trees fully independent with variance σ², their "
        "average would have variance σ²/B.")

    # --- 6.3 Gradient Boosting ---
    add_heading(doc, "6.3 Gradient Boosting", level=2)
    add_para(doc,
        "Gradient Boosting also builds many trees, but sequentially rather than independently. "
        "Each new tree is fitted to the error left behind by all previous trees. Beginning from "
        "a constant prediction, the model is refined in stages:")
    add_equation(doc, "F₀(x) = mean(y)", "Equation 6: the initial prediction.")
    add_equation(doc, "Fₘ(x) = Fₘ₋₁(x) + ν · hₘ(x)",
                 "Equation 7: stage m adds a new tree hₘ scaled by the learning rate ν.")
    add_para(doc,
        "The tree hₘ is fitted to the negative gradient of the loss with respect to the current "
        "prediction. For squared-error loss this reduces to the plain residual:")
    add_equation(doc, "rᵢₘ = −[ ∂L(yᵢ, F(xᵢ)) / ∂F(xᵢ) ]  = yᵢ − Fₘ₋₁(xᵢ)",
                 "Equation 8: pseudo-residuals — what the next tree is asked to predict.")
    add_para(doc,
        "Where Random Forest averages independent guesses, boosting builds a chain of "
        "corrections. On structured tabular data this usually performs better, and it does here.")

    # --- 6.4 SVR ---
    add_heading(doc, "6.4 Support Vector Regression (SVR)", level=2)
    add_para(doc,
        "Support Vector Regression fits a tube of width ε around the data and penalises only the "
        "points falling outside it. Predictions inside the tube incur no loss at all — the "
        "ε-insensitive loss:")
    add_equation(doc, "Lε(y, ŷ) = max(0, |y − ŷ| − ε)",
                 "Equation 9: errors smaller than ε are ignored entirely.")
    add_para(doc,
        "The optimisation balances a flat, low-complexity function against the size of the "
        "errors that do fall outside the tube:")
    add_equation(doc, "minimise  ½‖w‖² + C Σᵢ (ξᵢ + ξᵢ*)",
                 "Equation 10: C sets the trade-off; ξ are slack variables for points outside the tube.")
    add_para(doc,
        "Non-linear relationships are captured using the kernel trick, which measures similarity "
        "in a higher-dimensional space without ever constructing that space. This project uses "
        "the Radial Basis Function (RBF) kernel:")
    add_equation(doc, "K(xᵢ, xⱼ) = exp(−γ ‖xᵢ − xⱼ‖²)",
                 "Equation 11: the RBF kernel — similarity decays with squared distance.")
    add_comment(doc,
        "Strong viva point: because the RBF kernel is distance-based, and because C and ε are "
        "expressed in target units, SVR required BOTH the features and the target to be scaled. "
        "Without target scaling it scored R² = −0.02, i.e. worse than always predicting the "
        "mean. Wrapping it in TransformedTargetRegressor with a StandardScaler raised it to 0.85.")

    # --- 6.5 Voting ---
    add_heading(doc, "6.5 Voting Ensemble", level=2)
    add_para(doc,
        "A Voting Regressor combines several fitted models by averaging their predictions. This "
        "project averages Linear Regression, Random Forest and Gradient Boosting:")
    add_equation(doc, "ŷ_voting = (1/K) Σ_{k=1..K} ŷ_k(x)",
                 "Equation 12: unweighted mean of the K = 3 base models.")
    add_para(doc,
        "Different algorithms tend to fail on different records, so averaging cancels part of "
        "the error. Its weakness is that every member counts equally, so a weak member drags "
        "the ensemble down.")

    # --- 6.6 Stacking ---
    add_heading(doc, "6.6 Stacking Ensemble", level=2)
    add_para(doc,
        "Stacking addresses exactly that weakness. Rather than a fixed average, a second-level "
        "model — the meta-learner — is trained to learn how much to trust each base model:")
    add_equation(doc, "ŷ_stacking = g( ŷ₁(x), ŷ₂(x), …, ŷ_K(x) )",
                 "Equation 13: the meta-learner g combines the base predictions.")
    add_para(doc,
        "Here g is Ridge Regression — least squares with an L2 penalty that keeps the "
        "combination weights small and stable:")
    add_equation(doc, "β̂_ridge = argmin { Σᵢ (yᵢ − βᵀzᵢ)² + λ‖β‖² }",
                 "Equation 14: zᵢ is the vector of base-model predictions for sample i.")
    add_para(doc,
        "To stop the meta-learner from simply trusting base models that have already seen the "
        "training rows, the base predictions are generated by cross-validation. This makes "
        "stacking the most expensive model in the project to train.")

    # --- 6.7 Summary ---
    add_heading(doc, "6.7 Summary of Models", level=2)
    add_table(doc, ["Model", "Type", "Key idea", "Hyper-parameters"], [
        ["Linear Regression", "Linear", "Weighted sum of features", "None (closed form)"],
        ["Random Forest", "Bagging ensemble", "Mean of 100 decorrelated trees", "n_estimators = 100"],
        ["Gradient Boosting", "Boosting ensemble", "Sequential error correction", "n_estimators = 100"],
        ["Support Vector Regression", "Kernel method", "ε-tube with RBF kernel", "C = 1.0, ε = 0.1"],
        ["Voting Ensemble", "Ensemble", "Mean of 3 base models", "3 base estimators"],
        ["Stacking Ensemble", "Ensemble", "Ridge meta-learner over 3 bases", "Ridge final estimator"],
    ], widths=[1.6, 1.3, 2.0, 1.5])
