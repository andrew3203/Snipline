INSERT INTO subscription_plan (id, name, description, price_usd, days_duration, features)
VALUES
(1, 'Basic', 'Базовая подписка на 1 месяц', 5.0, 30,
 '{
    "reports_per_day": 2,
    "filter_limit": 1,
    "can_change_filters": false,
    "detailed_report_requests_per_day": 0,
    "follow_up_questions_enabled": false
 }'::jsonb),
(2, 'Standard', 'Стандартная подписка на 1 месяц', 15.0, 30,
 '{
    "reports_per_day": 2,
    "filter_limit": 2,
    "can_change_filters": false,
    "detailed_report_requests_per_day": 1,
    "follow_up_questions_enabled": false
 }'::jsonb),
(3, 'Premium', 'Премиум подписка на 1 месяц', 25.0, 30,
 '{
    "reports_per_day": 2,
    "filter_limit": null,
    "can_change_filters": true,
    "detailed_report_requests_per_day": 30,
    "follow_up_questions_enabled": true
 }'::jsonb),
(4, 'Basic', 'Базовая подписка на 6 месяцев', 27.0, 180,
 '{
    "reports_per_day": 2,
    "filter_limit": 1,
    "can_change_filters": false,
    "detailed_report_requests_per_day": 0,
    "follow_up_questions_enabled": false
 }'::jsonb),
(5, 'Standard', 'Стандартная подписка на 6 месяцев', 80.0, 180,
 '{
    "reports_per_day": 2,
    "filter_limit": 2,
    "can_change_filters": false,
    "detailed_report_requests_per_day": 1,
    "follow_up_questions_enabled": false
 }'::jsonb),
(6, 'Premium', 'Премиум подписка на 6 месяцев', 130.0, 180,
 '{
    "reports_per_day": 2,
    "filter_limit": null,
    "can_change_filters": true,
    "detailed_report_requests_per_day": 30,
    "follow_up_questions_enabled": true
 }'::jsonb),
 (7, 'PremiumGift', 'Премиум подписка на 3 дня', 0, 3,
 '{
    "reports_per_day": 2,
    "filter_limit": null,
    "can_change_filters": true,
    "detailed_report_requests_per_day": 30,
    "follow_up_questions_enabled": true
 }'::jsonb);
