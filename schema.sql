-- Create lists table
CREATE TABLE IF NOT EXISTS lists (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT DEFAULT 'Untitled List',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    expiry_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now() + interval '7 days') NOT NULL
);

-- Create items table
CREATE TABLE IF NOT EXISTS items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    list_id UUID REFERENCES lists(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS items_list_id_idx ON items(list_id);
CREATE INDEX IF NOT EXISTS lists_code_idx ON lists(code);

-- Enable Row-Level Security
ALTER TABLE lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY "Allow public read access to lists" 
    ON lists FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to lists" 
    ON lists FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update access to lists" 
    ON lists FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow public delete access to lists" 
    ON lists FOR DELETE USING (true);

CREATE POLICY "Allow public read access to items" 
    ON items FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to items" 
    ON items FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update access to items" 
    ON items FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow public delete access to items" 
    ON items FOR DELETE USING (true); 