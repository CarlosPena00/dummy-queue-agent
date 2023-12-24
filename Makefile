include micromamba.mk
micromamba.mk:
	curl \
		--output micromamba.mk \
		--location \
		"https://raw.githubusercontent.com/giovannipcarvalho/micromamba.mk/master/micromamba.mk"
