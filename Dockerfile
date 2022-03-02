FROM eeacms/plone-backend:6.0.0-1
ENV PROFILES="eea.kitkat:default eea.progress.workflow:default eea.dexterity.indicators:default eea.dexterity.themes:default"

COPY requirements.txt constraints.txt /app/
RUN ./bin/pip install -r requirements.txt -c constraints.txt ${PIP_PARAMS}
