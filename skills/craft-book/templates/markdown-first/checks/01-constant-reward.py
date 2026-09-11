"""Chapter 1 worked example and checkpoint 1.2; Appendix A checkpoint A.1."""
assert abs(1 / (1 - 0.9) - 10) < 1e-12
assert abs(1 / (1 - 0.99) - 100) < 1e-9
posterior = 0.30 * 0.80 / (0.30 * 0.80 + 0.70 * 0.10)
assert abs(posterior - 0.774) < 5e-4, posterior
posterior_small_prior = 0.05 * 0.80 / (0.05 * 0.80 + 0.95 * 0.10)
assert abs(posterior_small_prior - 0.296) < 5e-4, posterior_small_prior
