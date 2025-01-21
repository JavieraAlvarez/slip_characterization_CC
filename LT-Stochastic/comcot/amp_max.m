% graficos y archivos .xyz de amplitudes maximas y mapas de inundacion

function amp_max(startstep, endstep, step_int, grid_id, tol)
% startstep: tiempo inicial
% endstep: tiempo final
% step_int: paso de tiempo
% grid_id: numero de grilla
% tol: tolerancia (usar 0 o 0.05)



grid_id_str = num2str(grid_id);
if length(grid_id_str)==1
    str_id = strcat('0',num2str(grid_id));
else
    str_id = num2str(grid_id);
end

N = round((endstep - startstep)/step_int)+1;
time = startstep;

layerx = load(strcat('layer',str_id,'_x.dat'));
layery = load(strcat('layer',str_id,'_y.dat'));
layer  = load(strcat('layer',str_id,'.dat'));

filename_head = strcat('z_',str_id,'_');

nx = length(layerx);
ny = length(layery);

layer = reshape(layer,nx,ny);
disp('Datos cargados')
%amplitud maxima

amp = zeros(nx,ny);

for k= 1:N
 step = time;
    if step < 10
        filename_minute = strcat('00000',num2str(step));
    end
    if step >=10 && step < 100
        filename_minute = strcat('0000',num2str(step));
    end
    if step >=100 && step < 1000
        filename_minute = strcat('000',num2str(step));
    end

    if step >=1000 && step < 10000
        filename_minute = strcat('00',num2str(step));
    end
    if step >=10000 && step < 100000
        filename_minute = strcat('0',num2str(step));
    end
    if step >=100000
        filename_minute = strcat(num2str(step));
    end
	
	
    filename = [char(filename_head),num2str(filename_minute),'.dat'];
	
	fid = fopen(char(filename));
    a = fscanf(fid,'%g',inf); % write all data into a column of matrix a.
    fclose(fid);
    region = reshape(a,nx,ny);
    clear a
	
	for i = 1:nx
		for j = 1:ny
			if amp(i,j) < region(i,j)
				amp(i,j) = region(i,j);
			end
		end
	end
	time = time + step_int;
end
amp = amp';

% guarda amplitud maxima en xyz
disp('')


k = 1;
amp_z = ones(ny,nx);
for q = 1 : ny
	for w = 1: nx
		amp_z(k) = amp(q,w);
		k = k+1;
	end
end

k = 1;
mm1 = [];
mm2 = [];
mm3 = [];


for i = 1 : ny
    for j = 1 : 1 : nx
        mm1(k) = layerx(j);
        mm2(k) = layery(i);
        mm3(k) = amp_z(k);
        k = k+1;
    end
end

mm = [mm1' mm2' mm3'];

fid = fopen('amp_max_xyz.xyz','w+');

for i1 = 1:length(mm)
	fprintf(fid,'%20.10f %20.10f %20.10f\n',mm(i1,:));
end
fclose(fid);

disp('Archivos de Amplitudes Guardados')
% figura de amplitud maxima

[x,y] = meshgrid(layerx,layery);
cmax = max(max(amp));

figure
pcolor(x,y,amp)
shading interp
axis equal
axis tight
caxis([-cmax cmax]);
colorbar
title('Max Amp')
%figurename = ['Figure_Max_Amp.png'];
figurename = strcat('Figure_Max_Amp_Layer_',str_id,'.png');
print('-dpng', figurename);

% Calculo de inundacion


amp =amp';

inundation=zeros(nx,ny);
for i=1:nx
    for j=1:ny
        if amp(i,j)+layer(i,j)<= amp(i,j) && amp(i,j)+layer(i,j) > tol
            inundation(i,j)=amp(i,j)+layer(i,j);
        end
    end
end
inundation = inundation';

%guarda inundacion en xyz

k = 1;
inund_z = ones(ny,nx);
for q = 1 : ny
	for w = 1: nx
		inund_z(k) = inundation(q,w);
		k = k+1;
	end
end

k = 1;
mm1 = [];
mm2 = [];
mm3 = [];

for i = 1 : ny
    for j = 1 : 1 : nx
        mm1(k) = layerx(j);
        mm2(k) = layery(i);
        mm3(k) = inund_z(k);
        k = k+1;
    end
end

mm = [mm1' mm2' mm3'];

fid = fopen('inundacion_xyz.xyz','w+');

for i1 = 1:length(mm)
	fprintf(fid,'%20.10f %20.10f %20.10f\n',mm(i1,:));
end
fclose(fid);

disp('Archivo Inundacion Guardado')
%dibujo inundacion

cmax = max(max(inundation));

figure
pcolor(x,y,inundation)
shading interp
axis equal
axis tight
caxis([-cmax cmax]);
colorbar
title('Inundacion')
hold on
contour(x,y,-layer',[0 0],'k')
%figurename = ['Figure_Inundacion.png'];
figurename = strcat('Figure_Inundacion_Layer',str_id,'.png');
print('-dpng', figurename);