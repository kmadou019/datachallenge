<template>
  <div class="w-full h-screen flex justify-center overflow-hidden">
    <div class="w-full h-full overflow-auto">
      <div class="w-full h-fit flex flex-col">
        <div class="w-full h-screen relative flex justify-center">
          <div class="w-full h-full overflow-hidden relative">
            <div class="w-full h-full bg-gradient-to-t from-primary/60 to-slate-900/40 absolute"></div>
            <img src="@/assets/images/test1.jpg" class="w-full h-full object-cover" alt="">
          </div>
          <div class="w-full h-screen max-w-screen-2xl absolute px-8 flex flex-col items-center">
            <nav-bar />
            <div class="w-full  grow flex flex-col justify-center items-center gap-12">
              <span class="text-6xl font-bold text-white text-center">
                Prépare ton Examen
              </span>
            
              <span class="text-center text-white text-lg leading-relaxed">
                Une <span class="font-semibold ">plateforme éco-responsable</span>, alimentée par l'IA, qui aide les étudiants 
                à préparer leurs examens de <span class="font-semibold">propriété intellectuelle</span> et de certification professionnelle.  
                <br>
                <br>
                <span class="font-bold text-xl">BrevetLib </span> te plonge dans une bibliothèque numérique riche en 
                <span class="font-semibold ">ressources, articles</span> et supports d’apprentissage.
                <br>
                <br>
                Explore des sujets variés, de la théorie aux recherches avancées, et 
                <span class="font-semibold">booste tes connaissances</span>.
                <br>
                <br>
                Rejoins-nous et ouvre la porte à un avenir fondé sur 
                <span class="font-semibold">le savoir et l’innovation</span>.
              </span>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

import navBar from '@/components/commun/navBar.vue'




</script>
