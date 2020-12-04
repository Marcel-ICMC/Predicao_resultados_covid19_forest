--- Luiz ---
--QUESTAO 1
---a
SELECT COUNT(*) FROM PACIENTE;
---b 
Select ic_sexo, count(ic_sexo)  
	from paciente  
	group by paciente.ic_sexo 
	having UPPER(paciente.IC_SEXO) = 'M' 
		or UPPER(paciente.IC_SEXO) = 'F';


-- QUESTAO 2 

-- a POR FAIXA ETARIA
SELECT 
	COUNT(P.IC_SEXO) FILTER (where UPPER(P.IC_SEXO) = 'F') as FEMALE,
	COUNT(P.IC_SEXO) FILTER (where UPPER(P.IC_SEXO) = 'M') as MALE,
	FLOOR((date_part('year', CURRENT_DATE)-P.AA_NASCIMENTO::INTEGER)/10) || '0s' as DECADA
FROM PACIENTE P
WHERE P.AA_NASCIMENTO SIMILAR TO '%(0|9)%'
GROUP BY DECADA;

--- c por decada 
with ages as (
	select min(date_part('year', CURRENT_DATE)- P.AA_NASCIMENTO::int)::int as min_age,
           max(date_part('year', CURRENT_DATE)- P.AA_NASCIMENTO::int)::int as max_age
	from PACIENTE P
	WHERE P.AA_NASCIMENTO SIMILAR TO '%(0|9)%'
),
     histogram as (
   select width_bucket((date_part('year', CURRENT_DATE)- P.AA_NASCIMENTO::int), 
					   min_age, max_age, 9) as bucket,
          int4range(min(date_part('year', CURRENT_DATE)- P.AA_NASCIMENTO::int)::int, 
					max(date_part('year', CURRENT_DATE)- P.AA_NASCIMENTO::int)::int, '[]') as range,
        COUNT(P.IC_SEXO) FILTER (where UPPER(P.IC_SEXO) = 'F') as FEMALE,
		COUNT(P.IC_SEXO) FILTER (where UPPER(P.IC_SEXO) = 'M') as MALE
     from paciente P, ages
		 WHERE P.AA_NASCIMENTO SIMILAR TO '%(0|9)%'
 group by bucket
 order by bucket
)
 select bucket, range, FEMALE, MALE
   from histogram;


-- Questao 3. Qual a maior quantidade de exames solicitados para um ´unico paciente ? 
SELECT id_paciente, count(distinct id_exame) FROM exames group by id_paciente ORDER BY 2 DESC LIMIT 1
-- ou
SELECT id_paciente, COUNT(*) FROM (SELECT DISTINCT id_exame, id_paciente FROM exames) AS temp group by temp.id_paciente ORDER BY 2 DESC LIMIT 1;

"d5aef7e019e21e760b0a88f6a97526de6496a58f" = 10271

-- Questao 4. Qual é a média de exames pedidos para homens e para mulheres? 
with totalPacientes as (
	Select ic_sexo as sexo, count(ic_sexo) as total 
		from paciente  
		group by paciente.ic_sexo 
		having UPPER(paciente.IC_SEXO) = 'M' 
			or UPPER(paciente.IC_SEXO) = 'F'
),
	totalExames as(
	Select ic_sexo as sexo, count(id_exame) as total_exame 
	from (exames inner join paciente on exames.id_paciente = paciente.id_paciente) 
		group by paciente.ic_sexo 
		having UPPER(paciente.IC_SEXO) = 'M' or UPPER(paciente.IC_SEXO) = 'F'
)
 select tp.sexo, te.total_exame/tp.total as media_exames
   from totalPacientes as tp, totalExames as te where tp.sexo = te.sexo ;

-- Questao 5. 

Select * from exames
-- total de pacientes 332117


-- Paciente
-- id_paciente, ic_sexo, aa_nascimento

Select * from exames
Select count(1) from exames
-- total de exames 9919910

-- Exames
-- 

select distinct(de_exame), count(de_exame) from exames group by de_exame having count(de_exame) > 1000

select count(distinct(de_exame)) from exames
-- total de exames distintos 1361

   
   