FROM nginx:stable-alpine

# Удаляем стандартный конфиг Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Копируем твой конфиг внутрь контейнера
# (Путь nginx.conf относительный, так как контекст сборки будет внутри папки nginx или корня)
COPY nginx.conf /etc/nginx/conf.d/default.conf
