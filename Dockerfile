FROM eeacms/plone-backend:6.0.0-28
ENV PROFILES="eea.website.policy:default"

COPY requirements.txt constraints.txt /app/
RUN ./bin/pip install -r requirements.txt -c constraints.txt ${PIP_PARAMS} \
 && find /app -not -user plone -exec chown plone:plone {} \+
