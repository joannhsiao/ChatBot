$(document).ready(function() {			
            var canvas = document.getElementById("c");
			var ctx = canvas.getContext("2d");
			var c = $("#c");
			var w,h;
			var pi = Math.PI;
			var all_attribute = {
				num:100,            			 // 個數
				start_probability:0.1,		     // 如果數量小於num，有這些幾率添加一個新的     		     
				size_min:1,   			     // 初始愛心大小的最小值
				size_max:2,   			     // 初始愛心大小的最大值
				size_add_min:0.3,               // 每次變大的最小值（就是速度）
				size_add_max:0.5,               // 每次變大的最大值
				opacity_min:0.3,                 // 初始透明度最小值
				opacity_max:0.5, 				 // 初始透明度最大值
				opacity_prev_min:.003,            // 透明度遞減值最小值
				opacity_prev_max:.005,            // 透明度遞減值最大值
				light_min:0,                 	  // 顏色亮度最小值
				light_max:90,                 	  // 顏色亮度最大值
			};
			var style_color = find_random(0,360);  
			var all_element =[];
			window_resize();
			function start(){
				window.requestAnimationFrame(start);
				style_color += 0.1;
				//更改背景色hsl(顏色值，飽和度，明度)
				ctx.fillStyle = 'hsl(' + style_color + ',100%,97%)';
				ctx.fillRect(0, 0, w, h);
				if (all_element.length < all_attribute.num && Math.random() < all_attribute.start_probability){
					all_element.push(new ready_run);
				}
				all_element.map(function(line) {
					line.to_step();
				})
			}
			function ready_run(){
				this.to_reset();
			}
			function arc_heart(x,y,z,m){
				//繪制愛心圖案的方法，參數x,y是愛心的初始坐標，z是愛心的大小，m是愛心上升的速度
				//愛心向左飄
				//x += m;
				//愛心向右飄
				//x -= m;
				//愛心向上飄，向下飄換成+
				y -= m * 10;
				 
				ctx.moveTo(x,y);
				z *= 0.05;
				ctx.bezierCurveTo(x, y - 3 * z, x - 5 * z, y - 15 * z, x - 25 * z, y - 15 * z);
				ctx.bezierCurveTo(x - 55 * z, y - 15 * z, x - 55 * z, y + 22.5 * z, x - 55 * z, y + 22.5 * z);
				ctx.bezierCurveTo(x - 55 * z, y + 40 * z, x - 35 * z, y + 62 * z, x, y + 80 * z);
				ctx.bezierCurveTo(x + 35 * z, y + 62 * z, x + 55 * z, y + 40 * z, x + 55 * z, y + 22.5 * z);
				ctx.bezierCurveTo(x + 55 * z, y + 22.5 * z, x + 55 * z, y - 15 * z, x + 25 * z, y - 15 * z);
				ctx.bezierCurveTo(x + 10 * z, y - 15 * z, x, y - 3 * z, x, y);
	      	}
			ready_run.prototype = {
				to_reset:function(){
					var t = this;
					t.x = find_random(0, w);
					t.y = find_random(0, h);
					t.size = find_random(all_attribute.size_min, all_attribute.size_max);
					t.size_change = find_random(all_attribute.size_add_min, all_attribute.size_add_max);
					t.opacity = find_random(all_attribute.opacity_min, all_attribute.opacity_max);
					t.opacity_change = find_random(all_attribute.opacity_prev_min, all_attribute.opacity_prev_max);
					t.light = find_random(all_attribute.light_min, all_attribute.light_max);
					t.color = 'hsl(' + style_color + ',100%,' + t.light + '%)';
				},
				to_step:function(){
					var t = this;
					t.opacity -= t.opacity_change;
					t.size += t.size_change;
					if(t.opacity <= 0){
						t.to_reset();
						return false;
					}
					ctx.fillStyle = t.color;
					ctx.globalAlpha = t.opacity;
					ctx.beginPath();
					arc_heart(t.x, t.y, t.size, t.size);
					ctx.closePath();
					ctx.fill();
					ctx.globalAlpha = 1;
				}
			}
			
			function window_resize(){
//				canvas鋪滿窗口
				w = window.innerWidth;
				h = window.innerHeight;
				//如果需要鋪滿內容可以換下面這個
//				w=$("body").width();
//				h=$("body").height();
				canvas.width = w;
				canvas.height = h;
				
			}
			$(window).resize(function(){
				window_resize();
			});
			
			//返回一個介於參數1和參數2之間的隨機數
			function find_random(num_one,num_two){
				return Math.random() * (num_two - num_one) + num_one;
			}

			start();
        });