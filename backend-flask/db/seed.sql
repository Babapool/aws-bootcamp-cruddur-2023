-- this file was manually created
INSERT INTO public.users (display_name, email,handle, cognito_user_id)
VALUES
  ('Vitthal Kaul', 'vsk1734@gmail.com', 'babapool', 'MOCK'),
  ('Andrew Brown','vitthalsaikaul@hotmail.com' , 'andrewbrown' ,'MOCK'),
  ('Andrew Bayko','vitthalsai2001@outlook.com' , 'bayko' ,'MOCK'),
  ('Mycroft Holmes','mholmes@diogenes.com','mycroft','MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'andrewbrown' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )
