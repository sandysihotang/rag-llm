CREATE EXTENSION vector;

CREATE TABLE public.embedding (
	id bigserial NOT NULL,
	page_number int4 NOT NULL,
	source_file varchar(200) NOT NULL,
	files_id int NOT NULL,
	type_source int4 NULL,
	embedding_data public.vector NULL,
	sentence_chunk text NULL,
	create_time timestamptz DEFAULT now() NOT NULL,
	update_time timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT embedding_pkey PRIMARY KEY (id)
);
CREATE TABLE public.files (
    id bigserial not NULL,
    user_id int,
    file_name varchar(256),
	original_file_name varchar(256),
    status int,
	type_data int,
	create_time timestamptz DEFAULT now() NOT NULL,
	update_time timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT files_pkey PRIMARY KEY (id)
);

CREATE TABLE public.users(
	id bigserial not NULL,
    email varchar(256),
    password varchar(256),
	create_time timestamptz DEFAULT now() NOT NULL,
	update_time timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);


CREATE TABLE public.chat_history(
	id bigserial not NULL,
	user_id int,
	messages text,
	messages_from int,
	reference jsonb,
	context_answer text,
	create_time timestamptz DEFAULT now() NOT NULL,
	update_time timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT chat_history_pkey PRIMARY KEY (id)
);