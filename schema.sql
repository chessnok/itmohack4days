create table public."user"
(
    created_at      timestamp not null,
    id              serial
        primary key,
    email           varchar   not null,
    hashed_password varchar   not null
);

alter table public."user"
    owner to myuser;

create unique index ix_user_email
    on public."user" (email);

create table public.session
(
    created_at timestamp not null,
    id         varchar   not null
        primary key,
    user_id    integer   not null
        references public."user",
    name       varchar   not null
);

alter table public.session
    owner to myuser;

create table public.checkpoint_migrations
(
    v integer not null
        primary key
);

alter table public.checkpoint_migrations
    owner to myuser;

create table public.checkpoints
(
    thread_id            text                      not null,
    checkpoint_ns        text  default ''::text    not null,
    checkpoint_id        text                      not null,
    parent_checkpoint_id text,
    type                 text,
    checkpoint           jsonb                     not null,
    metadata             jsonb default '{}'::jsonb not null,
    primary key (thread_id, checkpoint_ns, checkpoint_id)
);

alter table public.checkpoints
    owner to myuser;

create index checkpoints_thread_id_idx
    on public.checkpoints (thread_id);

create table public.checkpoint_blobs
(
    thread_id     text                  not null,
    checkpoint_ns text default ''::text not null,
    channel       text                  not null,
    version       text                  not null,
    type          text                  not null,
    blob          bytea,
    primary key (thread_id, checkpoint_ns, channel, version)
);

alter table public.checkpoint_blobs
    owner to myuser;

create index checkpoint_blobs_thread_id_idx
    on public.checkpoint_blobs (thread_id);

create table public.checkpoint_writes
(
    thread_id     text                  not null,
    checkpoint_ns text default ''::text not null,
    checkpoint_id text                  not null,
    task_id       text                  not null,
    idx           integer               not null,
    channel       text                  not null,
    type          text,
    blob          bytea                 not null,
    task_path     text default ''::text not null,
    primary key (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

alter table public.checkpoint_writes
    owner to myuser;

create index checkpoint_writes_thread_id_idx
    on public.checkpoint_writes (thread_id);

create table public.file_objects
(
    id            varchar   not null
        primary key,
    file_name     varchar   not null,
    description   varchar   not null,
    created_by    varchar   not null,
    embedding     vector(256),
    session_id    varchar   not null,
    file_type     varchar   not null,
    s3_key        varchar   not null,
    s3_url        varchar   not null,
    created_at    timestamp not null,
    metadata_json text
);

alter table public.file_objects
    owner to myuser;

create table public.file_chunks
(
    id          varchar not null
        constraint "file_chunks _pkey"
            primary key,
    file_id     varchar not null,
    embedding   vector(256),
    content     varchar not null,
    chunk_index integer not null
);

alter table public.file_chunks
    owner to myuser;

create view public.v_file_chunks
            (id, file_id, chunk_index, content, embedding, file_name, file_type, session_id, created_by, metadata_json,
             created_at, description, s3_url, s3_key)
as
SELECT fc.id,
       fc.file_id,
       fc.chunk_index,
       fc.content,
       fc.embedding,
       fo.file_name,
       fo.file_type,
       fo.session_id,
       fo.created_by,
       fo.metadata_json,
       fo.created_at,
       fo.description,
       fo.s3_url,
       fo.s3_key
FROM file_chunks fc
         JOIN file_objects fo ON fo.id::text = fc.file_id::text;

alter table public.v_file_chunks
    owner to myuser;

