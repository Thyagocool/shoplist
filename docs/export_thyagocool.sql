-- ==============================================================
-- EXPORT dos dados de thyagocool@gmail.com
-- Gerado em: 12/07/2026
-- Para banco NOVO / vazio (sem dados existentes)
-- ==============================================================

-- 1. USUÁRIO
INSERT INTO users (id, name, email, password_hash)
VALUES (
  '6f1f06e6-cf0c-401c-a4a0-5a28a090c538',
  'Thyago',
  'thyagocool@gmail.com',
  '$2b$12$O8gzM5oUguSYGrRkJEmqH.qC4zreFXyR1Qb5BYSPItfM2uC7VH1iG'
);

-- 2. CATEGORIAS
INSERT INTO categories (id, name, user_id) VALUES
('8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'FRUTAS',         '6f1f06e6-cf0c-401c-a4a0-5a28a090c538'),
('08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'HIGIENE',        '6f1f06e6-cf0c-401c-a4a0-5a28a090c538'),
('ba6e0faf-8110-4f36-a209-243a54f3a8aa', 'LIMPEZA',        '6f1f06e6-cf0c-401c-a4a0-5a28a090c538'),
('6f8327c1-a98d-4dfe-91ad-49442401cdd5', 'NÃO PERECIVEIS', '6f1f06e6-cf0c-401c-a4a0-5a28a090c538'),
('01358eb8-1ae6-4801-980e-323b5846fc07', 'PERECÍVEIS',     '6f1f06e6-cf0c-401c-a4a0-5a28a090c538'),
('6e872bae-54fe-4b91-a434-f3f1f9762241', 'VERDURAS',       '6f1f06e6-cf0c-401c-a4a0-5a28a090c538');

-- 3. ITENS DO CATÁLOGO
INSERT INTO pre_registered_items (id, name, category_id, default_unit, default_quantity, min_stock, max_stock, user_id, active) VALUES
('f009e0f0-0c20-4de5-86c1-2ba14622adb6', 'ABACATE',                '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('572e4adc-a97c-4084-894c-f7f61145b650', 'ABACAXI',                '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('f8d199fa-99e6-4f93-850d-843e7ef7f5e5', 'ALFACE',                 '6e872bae-54fe-4b91-a434-f3f1f9762241', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('2cf4beb5-d1f2-4a25-a947-6a91880195df', 'AMACIANTE ROUPAS',       'ba6e0faf-8110-4f36-a209-243a54f3a8aa', 'un', 1.00, 1.00, 2.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('26c5ecff-b182-4377-8a81-33a10768d48c', 'ARROZ',                  '6f8327c1-a98d-4dfe-91ad-49442401cdd5', 'un', 1.00, 1.00, 3.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('f033aa60-ac1a-429a-8e64-a7c5e218155e', 'AÇUCAR',                 '6f8327c1-a98d-4dfe-91ad-49442401cdd5', 'un', 1.00, 1.00, 4.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('4258e971-91b3-44f8-b004-038578502bc9', 'BANANA',                 '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('c3f59911-f055-408e-bf88-9e1e5a4423be', 'BATATA',                 '6e872bae-54fe-4b91-a434-f3f1f9762241', 'un', 1.00, 3.00, 8.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('2ae8c94d-387f-4323-8623-087891e6e7a7', 'BATATA DOCE',            '6e872bae-54fe-4b91-a434-f3f1f9762241', 'un', 1.00, 1.00, 3.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('f3eb4ae9-9cc6-400e-ae91-393bcf921ba0', 'BETERRABA',              '6e872bae-54fe-4b91-a434-f3f1f9762241', 'un', 1.00, 1.00, 3.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('0fd30321-38cf-4553-8b27-6733d7687d9a', 'BROCOLIS',               '6e872bae-54fe-4b91-a434-f3f1f9762241', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('8d0d945b-3f2f-407f-863b-d3c0d85de75f', 'CAFÉ',                   '6f8327c1-a98d-4dfe-91ad-49442401cdd5', 'un', 1.00, 1.00, 4.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('279fd95c-90cc-4a5a-8fe1-1ebb5e856870', 'CARNE BIFE',             '01358eb8-1ae6-4801-980e-323b5846fc07', 'un', 1.00, 1.00, 1.50, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('9022c03e-6aeb-45c0-81d5-16409cdbbfe2', 'CARNE HAMBURGER',        '01358eb8-1ae6-4801-980e-323b5846fc07', 'un', 1.00, 1.00, 1.50, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('788bc0b3-fa37-4105-836b-569d4ce8c5dc', 'CEBOLA',                 '6e872bae-54fe-4b91-a434-f3f1f9762241', 'un', 1.00, 3.00, 8.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('7e60092d-0852-4ed6-90d3-d1033926e4a5', 'CENOURA',                '6e872bae-54fe-4b91-a434-f3f1f9762241', 'un', 1.00, 1.00, 2.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('1cf538b3-df00-455f-90bb-4c8bdf2b51f3', 'CONDICIONADOR FEMININO', '08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('0efdeb7a-1d27-4e0f-99bd-54fd00b3f5c4', 'CONDICIONADOR MASCULINO','08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('db2c0a68-ed18-4980-ae44-daa5f58a1b8d', 'CREME DENTAL',           '08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('8ea613fc-59bc-4d30-8254-99fffce10660', 'DESODORANTE  CORPO MASCULINO', '08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('5ca039ab-f03f-4463-8593-8bf2aef40c12', 'DESODORANTE CORPO FEMININO', '08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('ed37e38d-6a0f-4f4f-ba65-5c0ffb394df8', 'DETERGENTE LOUÇA',      'ba6e0faf-8110-4f36-a209-243a54f3a8aa', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('34ece8f3-0472-42f2-aa44-adb4d25e6545', 'FEIJÃO',                 '6f8327c1-a98d-4dfe-91ad-49442401cdd5', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('05aaa256-4fd8-4395-9e3d-6c3df367d43d', 'FRANGO PEITO',           '01358eb8-1ae6-4801-980e-323b5846fc07', 'un', 1.00, 1.00, 3.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('46f5e4d5-fe3f-41c1-9832-68eaff29d4f5', 'LARANJA',                '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 3.00, 5.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('6509d3e0-da86-4a27-b919-24c464273835', 'LEITE EM PÓ',            '6f8327c1-a98d-4dfe-91ad-49442401cdd5', 'un', 1.00, 1.00, 5.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('3a2dcd9a-aa04-4a57-8af0-48ae103dbb66', 'LEITE LUIZA',            '6f8327c1-a98d-4dfe-91ad-49442401cdd5', 'un', 1.00, 1.00, 2.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('5979e041-68c4-4b76-8ca6-464f611da1e3', 'MACARRÃO',               '6f8327c1-a98d-4dfe-91ad-49442401cdd5', 'un', 1.00, 1.00, 2.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('e608d5d6-2d4f-40a0-91b0-795045f471b3', 'MAMÃO',                  '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('7f570ec2-35d8-4948-bcc1-1f6cfa7081f9', 'MAÇÃ',                   '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 3.00, 5.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('cbda8f72-336a-4f0b-b46a-090045747f05', 'MORANGO',                '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('0da8b159-7c85-40e0-8dab-e9b9113bae46', 'SABAO LIQ. ROUPAS ',    'ba6e0faf-8110-4f36-a209-243a54f3a8aa', 'un', 1.00, 1.00, 2.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('6fb35ad3-f74a-48f3-a03c-47ed53d48c05', 'SABAO PÓ BANHEIRO',     'ba6e0faf-8110-4f36-a209-243a54f3a8aa', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('44c84315-49f2-4896-b0ac-57aeba9eacea', 'SABONETE BANHO',         '08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'un', 1.00, 1.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('82c66eb1-475f-4708-8ec9-aeb011f402f0', 'SABÃO BARRAS',           'ba6e0faf-8110-4f36-a209-243a54f3a8aa', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('a2415b8a-2ac8-4045-8379-208a4e0ff9a8', 'SABÃO LOUÇA',            'ba6e0faf-8110-4f36-a209-243a54f3a8aa', 'un', 1.00, 1.00, 5.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('83f17d76-476e-4180-afa6-8efd4da99d47', 'SHAMPOO FEMININO',       '08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('83692baf-4704-4319-a241-4a86228965fe', 'SHAMPOO MASCULINO',      '08d5b48a-46e3-4a88-b93b-624e0b3941e4', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('d18e5b38-bd69-47e9-8569-f75318245639', 'TANGIRINA',              '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 0.00, 5.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('856171b7-12ed-45db-8104-a1b1ea28d3c1', 'TOMATE',                 '6e872bae-54fe-4b91-a434-f3f1f9762241', 'un', 1.00, 2.00, 5.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true),
('1ae27c9a-4daf-455e-8ca9-d5e7b76e83d4', 'UVA',                    '8d810ee4-4e16-4cc1-ba0c-e612b099f8a9', 'un', 1.00, 0.00, 1.00, '6f1f06e6-cf0c-401c-a4a0-5a28a090c538', true);
